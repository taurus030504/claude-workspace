"""SQL for timeline events."""

from __future__ import annotations

import json
import sqlite3


def insert(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """INSERT INTO timeline_events (event_id, event_type, title, description, occurred_at, recorded_at,
               source_type, source_id, project_id, importance, metadata)
           VALUES (:event_id, :event_type, :title, :description, :occurred_at, :recorded_at,
               :source_type, :source_id, :project_id, :importance, :metadata)""",
        {**row, "metadata": json.dumps(row.get("metadata") or {}, ensure_ascii=False)},
    )


def latest_for_source(conn: sqlite3.Connection, source_type: str, source_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM timeline_events WHERE source_type = ? AND source_id = ? "
        "ORDER BY recorded_at DESC LIMIT 1",
        (source_type, source_id),
    ).fetchone()


def update_coalesced(conn: sqlite3.Connection, event_id: str, *, title: str, occurred_at: str, recorded_at: str, metadata: dict) -> None:
    conn.execute(
        "UPDATE timeline_events SET title = ?, occurred_at = ?, recorded_at = ?, metadata = ? WHERE event_id = ?",
        (title, occurred_at, recorded_at, json.dumps(metadata, ensure_ascii=False), event_id),
    )


def delete_for_source(conn: sqlite3.Connection, source_type: str, source_id: str) -> None:
    conn.execute("DELETE FROM timeline_events WHERE source_type = ? AND source_id = ?", (source_type, source_id))


def query(
    conn: sqlite3.Connection,
    *,
    start: str | None,
    end: str | None,
    event_types: list[str] | None,
    project_id: str | None,
    min_importance: int,
    before: tuple[str, str] | None,
    limit: int,
) -> list[sqlite3.Row]:
    sql = "SELECT * FROM timeline_events WHERE importance >= ?"
    params: list = [min_importance]
    if start:
        sql += " AND occurred_at >= ?"
        params.append(start)
    if end:
        sql += " AND occurred_at < ?"
        params.append(end)
    if event_types:
        sql += f" AND event_type IN ({','.join('?' * len(event_types))})"
        params += event_types
    if project_id:
        sql += " AND project_id = ?"
        params.append(project_id)
    if before:
        sql += " AND (occurred_at < ? OR (occurred_at = ? AND event_id < ?))"
        params += [before[0], before[0], before[1]]
    sql += " ORDER BY occurred_at DESC, event_id DESC LIMIT ?"
    params.append(limit)
    return conn.execute(sql, params).fetchall()


def count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT count(*) FROM timeline_events").fetchone()[0]
