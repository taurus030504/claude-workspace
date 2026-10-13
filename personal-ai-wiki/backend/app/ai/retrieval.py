"""Retrieval for chat: question -> ranked passages from enabled sources.

Phase 0 retrieves wiki chunks through keyword search. Memories, project data
and past conversations plug in here as further ``RetrievedPassage`` sources
in later phases; Phase 6 adds embedding search and merges the lists
(hybrid retrieval) before the context builder sees them.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.repositories import wiki_repo
from app.services.search_service import SearchService


@dataclass(frozen=True)
class RetrievedPassage:
    source_type: str  # wiki_page
    source_id: str
    title: str
    heading: str
    text: str
    score: float
    updated_at: str
    chunk_id: str | None = None
    revision: int | None = None
    char_start: int | None = None
    char_end: int | None = None


class Retriever:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.search = SearchService(conn)

    def retrieve(self, question: str, *, use_wiki: bool, top_k: int) -> list[RetrievedPassage]:
        passages: list[RetrievedPassage] = []
        if use_wiki:
            passages += self._wiki(question, top_k)
        passages.sort(key=lambda p: p.score, reverse=True)
        return passages[:top_k]

    def _wiki(self, question: str, top_k: int) -> list[RetrievedPassage]:
        result = self.search.search(question, entity_types=["wiki_page"], limit=top_k, group_by_entity=False)
        chunks = wiki_repo.get_chunks(self.conn, [h.chunk_id for h in result.items if h.chunk_id])
        pages = {
            r["page_id"]: r["updated_at"]
            for r in self.conn.execute(
                f"SELECT page_id, updated_at FROM wiki_pages WHERE page_id IN ({','.join('?' * len(result.items))})",
                [h.entity_id for h in result.items],
            )
        } if result.items else {}
        out: list[RetrievedPassage] = []
        for h in result.items:
            c = chunks.get(h.chunk_id or "")
            if c is None or not c["content"].strip():
                continue
            out.append(
                RetrievedPassage(
                    source_type="wiki_page",
                    source_id=h.entity_id,
                    title=c["title"],
                    heading=c["heading"],
                    text=c["content"],
                    score=h.score,
                    updated_at=pages.get(h.entity_id, ""),
                    chunk_id=c["chunk_id"],
                    revision=c["revision_number"],
                    char_start=c["char_start"],
                    char_end=c["char_end"],
                )
            )
        return out
