from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import search_service
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search(
    search: Annotated[SearchService, Depends(search_service)],
    q: Annotated[str, Query(min_length=1, max_length=500)],
    types: Annotated[str | None, Query(description="comma-separated entity types, e.g. wiki_page")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    group: Annotated[bool, Query(description="one hit per document")] = True,
):
    entity_types = [t.strip() for t in types.split(",") if t.strip()] if types else None
    return search.search(q, entity_types=entity_types, limit=limit, group_by_entity=group)
