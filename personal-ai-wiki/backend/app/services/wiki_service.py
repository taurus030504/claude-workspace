"""Knowledge Wiki: pages, revisions, chunking/indexing, trash.

Every write runs in one transaction that also updates the derived data
(chunks, search index) and records the timeline event, so the index can
never point at content that does not exist and vice versa.

Deletion is two-step:
  1. ``delete_page`` moves the page to the trash: hidden, removed from the
     search index and chunks, revisions kept, restorable.
  2. ``purge_page`` (only for trashed pages) removes the page, its revisions,
     tags, citations that quote it and its timeline events.
"""

from __future__ import annotations

import sqlite3

from app.config import Settings
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.ids import new_id
from app.core.timeutil import now_iso
from app.db.connection import transaction
from app.repositories import reference_repo, search_repo, tag_repo, timeline_repo, wiki_repo
from app.schemas.wiki import (
    FolderInfo,
    Page,
    PageCreate,
    PageList,
    PageSummary,
    PageUpdate,
    Revision,
    RevisionSummary,
    TagInfo,
)
from app.services.markdown_tools import chunk_markdown, excerpt, extract_wiki_links, normalize_text
from app.services.timeline_service import EventType, TimelineService

ENTITY = "wiki_page"


class WikiService:
    def __init__(self, conn: sqlite3.Connection, settings: Settings):
        self.conn = conn
        self.settings = settings
        self.timeline = TimelineService(conn)

    # ------------------------------------------------------------ reads
    def get_page(self, page_id: str, *, include_deleted: bool = True) -> Page:
        row = wiki_repo.get_page(self.conn, page_id)
        if row is None or (row["status"] == "deleted" and not include_deleted):
            raise NotFoundError(f"page {page_id} not found")
        return self._to_page(row)

    def list_pages(
        self,
        *,
        status: str = "active",
        folder: str | None = None,
        tag: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> PageList:
        rows = wiki_repo.list_pages(self.conn, status=status, folder=folder, tag=tag, limit=limit, offset=offset)
        tags = tag_repo.tags_for_many(self.conn, ENTITY, [r["page_id"] for r in rows])
        items = [
            PageSummary(
                page_id=r["page_id"],
                title=r["title"],
                folder=r["folder"],
                tags=tags[r["page_id"]],
                excerpt=excerpt(r["head"]),
                source_type=r["source_type"],
                current_revision=r["current_revision"],
                status=r["status"],
                content_length=r["content_length"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                deleted_at=r["deleted_at"],
            )
            for r in rows
        ]
        total = wiki_repo.count_pages(self.conn, status) if folder is None and tag is None else len(items)
        return PageList(items=items, total=total)

    def resolve_title(self, title: str) -> Page:
        row = wiki_repo.find_by_title(self.conn, " ".join(title.split()))
        if row is None:
            raise NotFoundError(f"no page titled '{title}'")
        return self._to_page(row)

    def list_revisions(self, page_id: str) -> list[RevisionSummary]:
        self._require(page_id)
        return [RevisionSummary(**dict(r)) for r in wiki_repo.list_revisions(self.conn, page_id)]

    def get_revision(self, page_id: str, number: int) -> Revision:
        self._require(page_id)
        r = wiki_repo.get_revision(self.conn, page_id, number)
        if r is None:
            raise NotFoundError(f"revision {number} of page {page_id} not found")
        return Revision(**dict(r), content_length=len(r["content"]))

    def list_folders(self) -> list[FolderInfo]:
        return [FolderInfo(**dict(r)) for r in wiki_repo.list_folders(self.conn)]

    def list_tags(self) -> list[TagInfo]:
        return [TagInfo(**dict(r)) for r in tag_repo.list_tags(self.conn)]

    # ------------------------------------------------------------ writes
    def create_page(
        self,
        data: PageCreate,
        *,
        source_type: str = "user",
        source_ref: str | None = None,
        author: str = "user",
    ) -> Page:
        content = self._check_content(data.content)
        title = normalize_text(data.title)
        now = now_iso()
        page_id = new_id()
        with transaction(self.conn):
            wiki_repo.insert_page(
                self.conn,
                {
                    "page_id": page_id,
                    "title": title,
                    "folder": data.folder,
                    "content": content,
                    "source_type": source_type,
                    "source_ref": source_ref,
                    "current_revision": 1,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            wiki_repo.insert_revision(
                self.conn, page_id=page_id, number=1, title=title, folder=data.folder, content=content,
                change_note=data.change_note, author=author, created_at=now,
            )
            tag_repo.set_tags(self.conn, ENTITY, page_id, data.tags, now)
            self._reindex(page_id, title, content, 1)
            self.timeline.record(
                EventType.WIKI_PAGE_CREATED,
                f"문서 생성: {title}",
                source_type=ENTITY,
                source_id=page_id,
                metadata={"revision": 1, "folder": data.folder, "via": source_type},
            )
        return self.get_page(page_id)

    def update_page(self, page_id: str, data: PageUpdate) -> Page:
        with transaction(self.conn):
            row = self._require(page_id)
            if row["status"] == "deleted":
                raise ConflictError("page is in the trash; restore it before editing")
            if data.expected_revision != row["current_revision"]:
                raise ConflictError(
                    "page was changed by someone else; reload before saving",
                    details={"current_revision": row["current_revision"]},
                )
            title = normalize_text(data.title) if data.title is not None else row["title"]
            folder = data.folder if data.folder is not None else row["folder"]
            content = self._check_content(data.content) if data.content is not None else row["content"]
            now = now_iso()
            changed = (title, folder, content) != (row["title"], row["folder"], row["content"])

            if data.tags is not None:
                current_tags = tag_repo.tags_for(self.conn, ENTITY, page_id)
                if [t.lower() for t in sorted(data.tags, key=str.lower)] != [t.lower() for t in current_tags]:
                    tag_repo.set_tags(self.conn, ENTITY, page_id, data.tags, now)
                    if not changed:
                        wiki_repo.touch_page(self.conn, page_id, now)

            if changed:
                revision = row["current_revision"] + 1
                wiki_repo.insert_revision(
                    self.conn, page_id=page_id, number=revision, title=title, folder=folder, content=content,
                    change_note=data.change_note, author="user", created_at=now,
                )
                wiki_repo.update_page_content(
                    self.conn, page_id, title=title, folder=folder, content=content, revision=revision, updated_at=now
                )
                if (title, content) != (row["title"], row["content"]):
                    self._reindex(page_id, title, content, revision)
                self.timeline.record(
                    EventType.WIKI_PAGE_UPDATED,
                    f"문서 수정: {title}",
                    source_type=ENTITY,
                    source_id=page_id,
                    metadata={"revision": revision},
                    coalesce=True,
                )
        return self.get_page(page_id)

    def restore_revision(self, page_id: str, number: int, expected_revision: int) -> Page:
        old = self.get_revision(page_id, number)
        return self.update_page(
            page_id,
            PageUpdate(
                expected_revision=expected_revision,
                title=old.title,
                folder=old.folder,
                content=old.content,
                change_note=f"리비전 {number} 복원",
            ),
        )

    def delete_page(self, page_id: str) -> Page:
        with transaction(self.conn):
            row = self._require(page_id)
            if row["status"] == "deleted":
                return self._to_page(row)
            now = now_iso()
            wiki_repo.set_status(self.conn, page_id, "deleted", now, now)
            wiki_repo.delete_chunks(self.conn, page_id)
            search_repo.remove_entity(self.conn, ENTITY, page_id)
            self.timeline.record(
                EventType.WIKI_PAGE_DELETED, f"문서 삭제(휴지통): {row['title']}", source_type=ENTITY, source_id=page_id
            )
        return self.get_page(page_id)

    def restore_page(self, page_id: str) -> Page:
        with transaction(self.conn):
            row = self._require(page_id)
            if row["status"] != "deleted":
                return self._to_page(row)
            now = now_iso()
            wiki_repo.set_status(self.conn, page_id, "active", None, now)
            self._reindex(page_id, row["title"], row["content"], row["current_revision"])
            self.timeline.record(
                EventType.WIKI_PAGE_RESTORED, f"문서 복원: {row['title']}", source_type=ENTITY, source_id=page_id
            )
        return self.get_page(page_id)

    def purge_page(self, page_id: str) -> None:
        with transaction(self.conn):
            row = self._require(page_id)
            if row["status"] != "deleted":
                raise ConflictError("move the page to the trash before deleting it permanently")
            search_repo.remove_entity(self.conn, ENTITY, page_id)
            tag_repo.remove_entity(self.conn, ENTITY, page_id)
            reference_repo.delete_by_source(self.conn, ENTITY, page_id)
            timeline_repo.delete_for_source(self.conn, ENTITY, page_id)
            wiki_repo.delete_page_row(self.conn, page_id)  # cascades to revisions and chunks

    def reindex_all(self) -> int:
        """Rebuild chunks and the wiki part of the search index from page content."""
        with transaction(self.conn):
            search_repo.remove_type(self.conn, ENTITY)
            rows = self.conn.execute(
                "SELECT page_id, title, content, current_revision FROM wiki_pages WHERE status = 'active'"
            ).fetchall()
            for r in rows:
                self._reindex(r["page_id"], r["title"], r["content"], r["current_revision"])
            self.conn.execute("DELETE FROM wiki_chunks WHERE page_id IN (SELECT page_id FROM wiki_pages WHERE status = 'deleted')")
        return len(rows)

    def index_is_consistent(self) -> bool:
        return search_repo.indexed_entity_count(self.conn, ENTITY) == wiki_repo.count_pages(self.conn, "active")

    # ------------------------------------------------------------ helpers
    def _reindex(self, page_id: str, title: str, content: str, revision: int) -> None:
        search_repo.remove_entity(self.conn, ENTITY, page_id)
        chunks = wiki_repo.replace_chunks(
            self.conn, page_id, revision, chunk_markdown(content, self.settings.chunk_max_chars)
        )
        for c in chunks:
            body = f"§ {c['heading']}\n{c['content']}" if c["heading"] else c["content"]
            search_repo.add(
                self.conn, entity_type=ENTITY, entity_id=page_id, chunk_id=c["chunk_id"], title=title, body=body
            )

    def _require(self, page_id: str) -> sqlite3.Row:
        row = wiki_repo.get_page(self.conn, page_id)
        if row is None:
            raise NotFoundError(f"page {page_id} not found")
        return row

    def _check_content(self, content: str) -> str:
        content = normalize_text(content)
        if len(content) > self.settings.max_page_chars:
            raise ValidationError(f"page content exceeds {self.settings.max_page_chars} characters")
        return content

    def _to_page(self, row: sqlite3.Row) -> Page:
        return Page(
            page_id=row["page_id"],
            title=row["title"],
            folder=row["folder"],
            content=row["content"],
            tags=tag_repo.tags_for(self.conn, ENTITY, row["page_id"]),
            summary=row["summary"],
            source_type=row["source_type"],
            source_ref=row["source_ref"],
            current_revision=row["current_revision"],
            status=row["status"],
            links=extract_wiki_links(row["content"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )
