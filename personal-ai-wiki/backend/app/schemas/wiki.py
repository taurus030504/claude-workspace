from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

MAX_TITLE = 300
MAX_TAGS = 30


def _clean_tags(tags: list[str] | None) -> list[str] | None:
    if tags is None:
        return None
    out: list[str] = []
    for t in tags:
        t = " ".join(t.strip().lstrip("#").split())
        if not t:
            continue
        if len(t) > 50:
            raise ValueError("tag longer than 50 characters")
        if t.lower() not in (x.lower() for x in out):
            out.append(t)
    if len(out) > MAX_TAGS:
        raise ValueError(f"at most {MAX_TAGS} tags")
    return out


def _clean_folder(folder: str | None) -> str | None:
    if folder is None:
        return None
    parts = [p.strip() for p in folder.replace("\\", "/").split("/")]
    if any(p in (".", "..") for p in parts):
        raise ValueError("folder may not contain '.' or '..'")
    return "/".join(p for p in parts if p)


class PageCreate(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_TITLE)
    content: str = ""
    folder: str = ""
    tags: list[str] = []
    change_note: str | None = Field(default=None, max_length=500)

    @field_validator("tags")
    @classmethod
    def _v_tags(cls, v):
        return _clean_tags(v)

    @field_validator("folder")
    @classmethod
    def _v_folder(cls, v):
        return _clean_folder(v)

    @field_validator("title")
    @classmethod
    def _title(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("title must not be blank")
        return v


class PageUpdate(BaseModel):
    """Partial update. ``expected_revision`` must equal the page's current revision
    (optimistic concurrency: a stale editor gets 409 instead of overwriting)."""

    expected_revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=MAX_TITLE)
    content: str | None = None
    folder: str | None = None
    tags: list[str] | None = None
    change_note: str | None = Field(default=None, max_length=500)

    @field_validator("tags")
    @classmethod
    def _v_tags(cls, v):
        return _clean_tags(v)

    @field_validator("folder")
    @classmethod
    def _v_folder(cls, v):
        return _clean_folder(v)

    @field_validator("title")
    @classmethod
    def _title(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = " ".join(v.split())
        if not v:
            raise ValueError("title must not be blank")
        return v


class PageSummary(BaseModel):
    page_id: str
    title: str
    folder: str
    tags: list[str]
    excerpt: str
    source_type: str
    current_revision: int
    status: str
    content_length: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


class Page(BaseModel):
    page_id: str
    title: str
    folder: str
    content: str
    tags: list[str]
    summary: str | None
    source_type: str
    source_ref: str | None
    current_revision: int
    status: str
    links: list[str] = Field(description="Targets of [[wiki links]] in the content")
    created_at: str
    updated_at: str
    deleted_at: str | None = None


class PageList(BaseModel):
    items: list[PageSummary]
    total: int


class RevisionSummary(BaseModel):
    revision_id: str
    revision_number: int
    title: str
    folder: str
    content_hash: str
    change_note: str | None
    author: str
    content_length: int
    created_at: str


class Revision(RevisionSummary):
    page_id: str
    content: str


class RevisionRestore(BaseModel):
    expected_revision: int = Field(ge=1)


class FolderInfo(BaseModel):
    folder: str
    page_count: int


class TagInfo(BaseModel):
    name: str
    usage: int
