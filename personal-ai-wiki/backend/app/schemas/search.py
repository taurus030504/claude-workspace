from __future__ import annotations

from pydantic import BaseModel


class SearchHit(BaseModel):
    entity_type: str  # wiki_page (memory, conversation, ... in later phases)
    entity_id: str
    chunk_id: str | None
    title: str
    heading: str
    snippet: str
    highlights: list[tuple[int, int]]  # [start, end) offsets into snippet
    matched_terms: list[str]
    score: float


class SearchResponse(BaseModel):
    query: str
    terms: list[str]
    tokenizer: str
    items: list[SearchHit]
