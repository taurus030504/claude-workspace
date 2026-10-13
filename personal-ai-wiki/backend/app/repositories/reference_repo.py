"""SQL for source_references (provenance / citations)."""

from __future__ import annotations

import json
import sqlite3

from app.core.ids import new_id


def add(
    conn: sqlite3.Connection,
    *,
    owner_type: str,
    owner_id: str,
    source_type: str,
    source_id: str,
    relation: str,
    quote: str | None,
    locator: dict,
    rank: int | None,
    created_at: str,
) -> None:
    conn.execute(
        """INSERT INTO source_references (reference_id, owner_type, owner_id, source_type, source_id,
               relation, quote, locator, rank, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (new_id(), owner_type, owner_id, source_type, source_id, relation, quote,
         json.dumps(locator, ensure_ascii=False), rank, created_at),
    )


def for_owners(conn: sqlite3.Connection, owner_type: str, owner_ids: list[str]) -> dict[str, list[sqlite3.Row]]:
    result: dict[str, list[sqlite3.Row]] = {i: [] for i in owner_ids}
    if not owner_ids:
        return result
    marks = ",".join("?" * len(owner_ids))
    for r in conn.execute(
        f"SELECT * FROM source_references WHERE owner_type = ? AND owner_id IN ({marks}) ORDER BY rank",
        [owner_type, *owner_ids],
    ):
        result[r["owner_id"]].append(r)
    return result


def delete_by_owner(conn: sqlite3.Connection, owner_type: str, owner_ids: list[str]) -> None:
    if owner_ids:
        marks = ",".join("?" * len(owner_ids))
        conn.execute(
            f"DELETE FROM source_references WHERE owner_type = ? AND owner_id IN ({marks})", [owner_type, *owner_ids]
        )


def delete_by_source(conn: sqlite3.Connection, source_type: str, source_id: str) -> None:
    conn.execute("DELETE FROM source_references WHERE source_type = ? AND source_id = ?", (source_type, source_id))
