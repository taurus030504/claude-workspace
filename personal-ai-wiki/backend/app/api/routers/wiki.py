from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.api.deps import wiki_service
from app.core.errors import PayloadTooLargeError
from app.schemas.wiki import (
    FolderInfo,
    Page,
    PageCreate,
    PageList,
    PageUpdate,
    Revision,
    RevisionRestore,
    RevisionSummary,
    TagInfo,
)
from app.services.file_import_service import FileImportService
from app.services.wiki_service import WikiService

router = APIRouter(prefix="/api/v1/wiki", tags=["wiki"])
Wiki = Annotated[WikiService, Depends(wiki_service)]


@router.get("/pages", response_model=PageList)
def list_pages(
    wiki: Wiki,
    status_: Annotated[Literal["active", "deleted"], Query(alias="status")] = "active",
    folder: str | None = None,
    tag: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return wiki.list_pages(status=status_, folder=folder, tag=tag, limit=limit, offset=offset)


@router.post("/pages", response_model=Page, status_code=status.HTTP_201_CREATED)
def create_page(body: PageCreate, wiki: Wiki):
    return wiki.create_page(body)


@router.get("/pages/{page_id}", response_model=Page)
def get_page(page_id: str, wiki: Wiki):
    return wiki.get_page(page_id)


@router.patch("/pages/{page_id}", response_model=Page)
def update_page(page_id: str, body: PageUpdate, wiki: Wiki):
    return wiki.update_page(page_id, body)


@router.delete("/pages/{page_id}", response_model=None, responses={200: {"model": Page}, 204: {}})
def delete_page(page_id: str, wiki: Wiki, permanent: bool = False):
    """Without ``permanent``: move to trash (restorable). With ``permanent=true``
    on a trashed page: remove it and everything derived from it."""
    if permanent:
        wiki.purge_page(page_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return wiki.delete_page(page_id)


@router.post("/pages/{page_id}/restore", response_model=Page)
def restore_page(page_id: str, wiki: Wiki):
    return wiki.restore_page(page_id)


@router.get("/pages/{page_id}/revisions", response_model=list[RevisionSummary])
def list_revisions(page_id: str, wiki: Wiki):
    return wiki.list_revisions(page_id)


@router.get("/pages/{page_id}/revisions/{number}", response_model=Revision)
def get_revision(page_id: str, number: int, wiki: Wiki):
    return wiki.get_revision(page_id, number)


@router.post("/pages/{page_id}/revisions/{number}/restore", response_model=Page)
def restore_revision(page_id: str, number: int, body: RevisionRestore, wiki: Wiki):
    return wiki.restore_revision(page_id, number, body.expected_revision)


@router.get("/resolve", response_model=Page)
def resolve_title(title: Annotated[str, Query(min_length=1, max_length=300)], wiki: Wiki):
    """Find the active page for a [[wiki link]] target (case-insensitive exact title)."""
    return wiki.resolve_title(title)


@router.get("/folders", response_model=list[FolderInfo])
def list_folders(wiki: Wiki):
    return wiki.list_folders()


@router.get("/tags", response_model=list[TagInfo])
def list_tags(wiki: Wiki):
    return wiki.list_tags()


@router.post("/import", response_model=Page, status_code=status.HTTP_201_CREATED)
async def import_file(
    wiki: Wiki,
    file: Annotated[UploadFile, File()],
    folder: Annotated[str, Form()] = "",
    tags: Annotated[str, Form(description="comma-separated")] = "",
):
    limit = wiki.settings.max_import_bytes
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise PayloadTooLargeError(f"file is larger than {limit // (1024 * 1024)} MB")
    tag_list = [t for t in (x.strip() for x in tags.split(",")) if t]
    body = PageCreate(title="import", folder=folder, tags=tag_list)  # reuse validation for folder/tags
    return await run_in_threadpool(
        FileImportService(wiki).import_file, file.filename or "untitled.txt", data, folder=body.folder, tags=body.tags
    )
