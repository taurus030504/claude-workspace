"""SQL for wiki pages, revisions and chunks."""

from __future__ import annotations

import sqlite3
from typing import Iterable

from app.core.ids import new_id
from app.services.markdown_tools import Chunk, sha256

PAGE_SUMMARY_COLS = (
    "page_id, title, folder, substr(content, 1, 400) AS head, source_type, current_revision, "
    "status, created_at, updated_at, deleted_at, length(content) AS content_length"
)


def get_page(conn: sqlite3.Connection, page_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM wiki_pages WHERE page_id = ?", (page_id,)).fetchone()


def list_pages(
    conn: sqlite3.Connection,
    *,
    status: str,
    folder: str | None,
    tag: str | None,
    limit: int,
    offset: int,
) -> list[sqlite3.Row]:
    sql = f"SELECT {PAGE_SUMMARY_COLS} FROM wiki_pages p WHERE status = ?"
    params: list = [status]
    if folder is not None:
        sql += " AND (folder = ? OR folder LIKE ? ESCAPE '\\')"
        params += [folder, escape_like(folder) + "/%"]
    if tag is not None:
        sql += (
            " AND EXISTS (SELECT 1 FROM entity_tags et JOIN tags t ON t.tag_id = et.tag_id"
            " WHERE et.entity_type = 'wiki_page' AND et.entity_id = p.page_id AND t.name = ?)"
        )
        params.append(tag)
    sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]
    return conn.execute(sql, params).fetchall()


def count_pages(conn: sqlite3.Connection, status: str = "active") -> int:
    return conn.execute("SELECT count(*) FROM wiki_pages WHERE status = ?", (status,)).fetchone()[0]


def find_by_title(conn: sqlite3.Connection, title: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM wiki_pages WHERE status = 'active' AND title = ? COLLATE NOCASE "
        "ORDER BY updated_at DESC LIMIT 1",
        (title,),
    ).fetchone()


def insert_page(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """INSERT INTO wiki_pages (page_id, title, folder, content, source_type, source_ref,
               current_revision, status, created_at, updated_at)
           VALUES (:page_id, :title, :folder, :content, :source_type, :source_ref,
               :current_revision, 'active', :created_at, :updated_at)""",
        row,
    )


def update_page_content(
    conn: sqlite3.Connection, page_id: str, *, title: str, folder: str, content: str, revision: int, updated_at: str
) -> None:
    conn.execute(
        "UPDATE wiki_pages SET title = ?, folder = ?, content = ?, current_revision = ?, updated_at = ? "
        "WHERE page_id = ?",
        (title, folder, content, revision, updated_at, page_id),
    )


def touch_page(conn: sqlite3.Connection, page_id: str, updated_at: str) -> None:
    conn.execute("UPDATE wiki_pages SET updated_at = ? WHERE page_id = ?", (updated_at, page_id))


def set_status(conn: sqlite3.Connection, page_id: str, status: str, deleted_at: str | None, updated_at: str) -> None:
    conn.execute(
        "UPDATE wiki_pages SET status = ?, deleted_at = ?, updated_at = ? WHERE page_id = ?",
        (status, deleted_at, updated_at, page_id),
    )


def delete_page_row(conn: sqlite3.Connection, page_id: str) -> None:
    conn.execute("DELETE FROM wiki_pages WHERE page_id = ?", (page_id,))


def insert_revision(
    conn: sqlite3.Connection,
    *,
    page_id: str,
    number: int,
    title: str,
    folder: str,
    content: str,
    change_note: str | None,
    author: str,
    created_at: str,
) -> str:
    revision_id = new_id()
    conn.execute(
        """INSERT INTO wiki_revisions (revision_id, page_id, revision_number, title, folder, content,
               content_hash, change_note, author, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (revision_id, page_id, number, title, folder, content, sha256(content), change_note, author, created_at),
    )
    return revision_id


def list_revisions(conn: sqlite3.Connection, page_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT revision_id, page_id, revision_number, title, folder, content_hash, change_note, author, "
        "created_at, length(content) AS content_length FROM wiki_revisions WHERE page_id = ? "
        "ORDER BY revision_number DESC",
        (page_id,),
    ).fetchall()


def get_revision(conn: sqlite3.Connection, page_id: str, number: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM wiki_revisions WHERE page_id = ? AND revision_number = ?", (page_id, number)
    ).fetchone()


def replace_chunks(conn: sqlite3.Connection, page_id: str, revision: int, chunks: Iterable[Chunk]) -> list[dict]:
    conn.execute("DELETE FROM wiki_chunks WHERE page_id = ?", (page_id,))
    rows = []
    for c in chunks:
        row = {
            "chunk_id": new_id(),
            "page_id": page_id,
            "revision_number": revision,
            "chunk_index": c.index,
            "heading": c.heading,
            "content": c.content,
            "char_start": c.start,
            "char_end": c.end,
            "content_hash": sha256(c.content),
        }
        conn.execute(
            """INSERT INTO wiki_chunks (chunk_id, page_id, revision_number, chunk_index, heading, content,
                   char_start, char_end, content_hash)
               VALUES (:chunk_id, :page_id, :revision_number, :chunk_index, :heading, :content,
                   :char_start, :char_end, :content_hash)""",
            row,
        )
        rows.append(row)
    return rows


def delete_chunks(conn: sqlite3.Connection, page_id: str) -> None:
    conn.execute("DELETE FROM wiki_chunks WHERE page_id = ?", (page_id,))


def get_chunks(conn: sqlite3.Connection, chunk_ids: list[str]) -> dict[str, sqlite3.Row]:
    if not chunk_ids:
        return {}
    marks = ",".join("?" * len(chunk_ids))
    rows = conn.execute(
        f"SELECT c.*, p.title FROM wiki_chunks c JOIN wiki_pages p ON p.page_id = c.page_id "
        f"WHERE c.chunk_id IN ({marks})",
        chunk_ids,
    ).fetchall()
    return {r["chunk_id"]: r for r in rows}


def chunk_ids_for_page(conn: sqlite3.Connection, page_id: str) -> list[str]:
    return [r[0] for r in conn.execute("SELECT chunk_id FROM wiki_chunks WHERE page_id = ?", (page_id,))]


def list_folders(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT folder, count(*) AS page_count FROM wiki_pages WHERE status = 'active' "
        "GROUP BY folder ORDER BY folder COLLATE NOCASE"
    ).fetchall()


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
