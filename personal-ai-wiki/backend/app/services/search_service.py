"""Keyword search over the shared FTS5 index.

Pipeline: analyze query -> FTS MATCH for terms the tokenizer can handle
(>= 3 chars with trigram) + substring scan for shorter terms -> rescore every
candidate by how many distinct terms it contains, title hits, frequency and
bm25 -> build a snippet with highlight offsets.

This class is the keyword half of the planned hybrid retrieval (Phase 6 adds
an embedding retriever and merges both result lists).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.repositories import search_repo
from app.schemas.search import SearchHit, SearchResponse
from app.services.text_analysis import analyze_query

SNIPPET_CHARS = 220
CANDIDATE_LIMIT = 300


@dataclass
class _Candidate:
    row: sqlite3.Row
    bm25: float


class SearchService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._tokenizer = search_repo.tokenizer(conn)

    @property
    def tokenizer(self) -> str:
        return self._tokenizer

    def search(
        self,
        query: str,
        *,
        entity_types: list[str] | None = None,
        limit: int = 20,
        group_by_entity: bool = True,
        max_per_entity: int = 2,
    ) -> SearchResponse:
        terms = analyze_query(query)
        hits = self._search_terms(terms, entity_types) if terms else []
        hits.sort(key=lambda h: h.score, reverse=True)
        per_entity: dict[str, int] = {}
        selected: list[SearchHit] = []
        cap = 1 if group_by_entity else max_per_entity
        for h in hits:
            n = per_entity.get(h.entity_id, 0)
            if n >= cap:
                continue
            per_entity[h.entity_id] = n + 1
            selected.append(h)
            if len(selected) >= limit:
                break
        return SearchResponse(query=query, terms=terms, tokenizer=self._tokenizer, items=selected)

    def _search_terms(self, terms: list[str], entity_types: list[str] | None) -> list[SearchHit]:
        if self._tokenizer == "trigram":
            fts_terms = [t for t in terms if len(t) >= 3]
            like_terms = [t for t in terms if len(t) < 3]
        else:
            # unicode61 cannot match inside Korean words; substring scan everything.
            fts_terms, like_terms = [], terms

        candidates: dict[int, _Candidate] = {}
        if fts_terms:
            for r in search_repo.match(self.conn, fts_terms, entity_types, CANDIDATE_LIMIT):
                candidates[r["rowid"]] = _Candidate(r, float(r["rank"]))
        if like_terms:
            for r in search_repo.like(self.conn, like_terms, entity_types, CANDIDATE_LIMIT):
                candidates.setdefault(r["rowid"], _Candidate(r, 0.0))

        return [h for c in candidates.values() if (h := _score(c, terms)) is not None]


def _score(c: _Candidate, terms: list[str]) -> SearchHit | None:
    title = c.row["title"] or ""
    body = c.row["body"] or ""
    title_l, body_l = title.lower(), body.lower()
    matched = [t for t in terms if t in title_l or t in body_l]
    if not matched:
        return None
    title_hits = sum(1 for t in matched if t in title_l)
    freq = sum(min(body_l.count(t), 5) for t in matched)
    coverage = len(matched) / len(terms)
    score = coverage * 10 + title_hits * 2 + freq * 0.3 + max(0.0, -c.bm25) * 0.5
    heading, _, text = body.partition("\n") if body.startswith("§ ") else ("", "", body)
    snippet, highlights = make_snippet(text or body, matched)
    return SearchHit(
        entity_type=c.row["entity_type"],
        entity_id=c.row["entity_id"],
        chunk_id=c.row["chunk_id"],
        title=title,
        heading=heading[2:] if heading else "",
        snippet=snippet,
        highlights=highlights,
        matched_terms=matched,
        score=round(score, 4),
    )


def make_snippet(text: str, terms: list[str], width: int = SNIPPET_CHARS) -> tuple[str, list[tuple[int, int]]]:
    lower = text.lower()
    positions = [p for t in terms if (p := lower.find(t)) >= 0]
    first = min(positions) if positions else 0
    start = max(0, first - width // 4)
    # Do not start in the middle of a word when we can avoid it.
    if start > 0:
        space = text.rfind(" ", max(0, start - 15), start)
        if space >= 0:
            start = space + 1
    end = min(len(text), start + width)
    window = text[start:end].replace("\n", " ")
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    snippet = prefix + window + suffix
    lw = snippet.lower()
    spans: list[tuple[int, int]] = []
    for t in terms:
        i = lw.find(t)
        while i >= 0:
            spans.append((i, i + len(t)))
            i = lw.find(t, i + len(t))
    spans.sort()
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return snippet, merged
