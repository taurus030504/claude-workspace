"""Tags shared by every entity type (wiki pages now; memories, projects, tasks later)."""

from __future__ import annotations

import sqlite3

from app.core.ids import new_id


def tags_for(conn: sqlite3.Connection, entity_type: str, entity_id: str) -> list[str]:
    return [
        r[0]
        for r in conn.execute(
            "SELECT t.name FROM entity_tags et JOIN tags t ON t.tag_id = et.tag_id "
            "WHERE et.entity_type = ? AND et.entity_id = ? ORDER BY t.name COLLATE NOCASE",
            (entity_type, entity_id),
        )
    ]


def tags_for_many(conn: sqlite3.Connection, entity_type: str, entity_ids: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {i: [] for i in entity_ids}
    if not entity_ids:
        return result
    marks = ",".join("?" * len(entity_ids))
    for r in conn.execute(
        f"SELECT et.entity_id, t.name FROM entity_tags et JOIN tags t ON t.tag_id = et.tag_id "
        f"WHERE et.entity_type = ? AND et.entity_id IN ({marks}) ORDER BY t.name COLLATE NOCASE",
        [entity_type, *entity_ids],
    ):
        result[r[0]].append(r[1])
    return result


def set_tags(conn: sqlite3.Connection, entity_type: str, entity_id: str, names: list[str], now: str) -> None:
    conn.execute("DELETE FROM entity_tags WHERE entity_type = ? AND entity_id = ?", (entity_type, entity_id))
    for name in names:
        row = conn.execute("SELECT tag_id FROM tags WHERE name = ?", (name,)).fetchone()
        tag_id = row[0] if row else new_id()
        if not row:
            conn.execute("INSERT INTO tags (tag_id, name, created_at) VALUES (?, ?, ?)", (tag_id, name, now))
        conn.execute(
            "INSERT OR IGNORE INTO entity_tags (tag_id, entity_type, entity_id, created_at) VALUES (?, ?, ?, ?)",
            (tag_id, entity_type, entity_id, now),
        )


def remove_entity(conn: sqlite3.Connection, entity_type: str, entity_id: str) -> None:
    conn.execute("DELETE FROM entity_tags WHERE entity_type = ? AND entity_id = ?", (entity_type, entity_id))


def list_tags(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT t.name, count(et.entity_id) AS usage FROM tags t "
        "LEFT JOIN entity_tags et ON et.tag_id = t.tag_id GROUP BY t.tag_id "
        "HAVING usage > 0 ORDER BY t.name COLLATE NOCASE"
    ).fetchall()
