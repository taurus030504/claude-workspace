"""SQL for the shared FTS5 ``search_index`` table."""

from __future__ import annotations

import sqlite3

from app.repositories.wiki_repo import escape_like

_COLS = "rowid, title, body, entity_type, entity_id, chunk_id"


def tokenizer(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'search_index'").fetchone()
    return "trigram" if row and "trigram" in row[0] else "unicode61"


def add(conn: sqlite3.Connection, *, entity_type: str, entity_id: str, chunk_id: str | None, title: str, body: str) -> None:
    conn.execute(
        "INSERT INTO search_index (title, body, entity_type, entity_id, chunk_id) VALUES (?, ?, ?, ?, ?)",
        (title, body, entity_type, entity_id, chunk_id),
    )


def remove_entity(conn: sqlite3.Connection, entity_type: str, entity_id: str) -> None:
    conn.execute("DELETE FROM search_index WHERE entity_type = ? AND entity_id = ?", (entity_type, entity_id))


def remove_type(conn: sqlite3.Connection, entity_type: str) -> None:
    conn.execute("DELETE FROM search_index WHERE entity_type = ?", (entity_type,))


def indexed_entity_count(conn: sqlite3.Connection, entity_type: str) -> int:
    return conn.execute(
        "SELECT count(DISTINCT entity_id) FROM search_index WHERE entity_type = ?", (entity_type,)
    ).fetchone()[0]


def _type_filter(entity_types: list[str] | None) -> tuple[str, list]:
    if not entity_types:
        return "", []
    return f" AND entity_type IN ({','.join('?' * len(entity_types))})", list(entity_types)


def match(conn: sqlite3.Connection, terms: list[str], entity_types: list[str] | None, limit: int) -> list[sqlite3.Row]:
    """FTS MATCH with OR of quoted terms; returns rows with a bm25 ``rank`` (lower is better)."""
    expr = " OR ".join('"' + t.replace('"', '""') + '"' for t in terms)
    type_sql, type_params = _type_filter(entity_types)
    return conn.execute(
        f"SELECT {_COLS}, bm25(search_index, 4.0, 1.0) AS rank FROM search_index "
        f"WHERE search_index MATCH ?{type_sql} ORDER BY rank LIMIT ?",
        [expr, *type_params, limit],
    ).fetchall()


def like(conn: sqlite3.Connection, terms: list[str], entity_types: list[str] | None, limit: int) -> list[sqlite3.Row]:
    """Substring scan for terms the tokenizer cannot match (shorter than 3 chars with trigram)."""
    conds = []
    params: list = []
    for t in terms:
        pattern = f"%{escape_like(t)}%"
        conds.append("title LIKE ? ESCAPE '\\' OR body LIKE ? ESCAPE '\\'")
        params += [pattern, pattern]
    type_sql, type_params = _type_filter(entity_types)
    return conn.execute(
        f"SELECT {_COLS}, 0.0 AS rank FROM search_index WHERE ({' OR '.join(conds)}){type_sql} LIMIT ?",
        [*params, *type_params, limit],
    ).fetchall()
