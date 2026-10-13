"""SQL for chat sessions and messages."""

from __future__ import annotations

import json
import sqlite3


def insert_session(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """INSERT INTO chat_sessions (session_id, title, origin, model, started_at, created_at, updated_at)
           VALUES (:session_id, :title, 'app', :model, :started_at, :created_at, :updated_at)""",
        row,
    )


def get_session(conn: sqlite3.Connection, session_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT s.*, (SELECT count(*) FROM chat_messages m WHERE m.session_id = s.session_id) AS message_count "
        "FROM chat_sessions s WHERE s.session_id = ?",
        (session_id,),
    ).fetchone()


def list_sessions(conn: sqlite3.Connection, *, origin: str | None, limit: int, offset: int) -> list[sqlite3.Row]:
    sql = (
        "SELECT s.*, (SELECT count(*) FROM chat_messages m WHERE m.session_id = s.session_id) AS message_count "
        "FROM chat_sessions s WHERE s.archived = 0"
    )
    params: list = []
    if origin:
        sql += " AND s.origin = ?"
        params.append(origin)
    sql += " ORDER BY s.updated_at DESC LIMIT ? OFFSET ?"
    return conn.execute(sql, [*params, limit, offset]).fetchall()


def count_sessions(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT count(*) FROM chat_sessions").fetchone()[0]


def update_session(conn: sqlite3.Connection, session_id: str, *, title: str | None = None, updated_at: str) -> None:
    if title is not None:
        conn.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE session_id = ?", (title, updated_at, session_id)
        )
    else:
        conn.execute("UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?", (updated_at, session_id))


def delete_session(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))


def message_ids(conn: sqlite3.Connection, session_id: str) -> list[str]:
    return [r[0] for r in conn.execute("SELECT message_id FROM chat_messages WHERE session_id = ?", (session_id,))]


def next_seq(conn: sqlite3.Connection, session_id: str) -> int:
    return conn.execute(
        "SELECT coalesce(max(seq), 0) + 1 FROM chat_messages WHERE session_id = ?", (session_id,)
    ).fetchone()[0]


def insert_message(conn: sqlite3.Connection, row: dict) -> None:
    conn.execute(
        """INSERT INTO chat_messages (message_id, session_id, seq, role, content, model, status,
               created_at, recorded_at, metadata)
           VALUES (:message_id, :session_id, :seq, :role, :content, :model, :status,
               :created_at, :recorded_at, :metadata)""",
        {**row, "metadata": json.dumps(row.get("metadata") or {}, ensure_ascii=False)},
    )


def list_messages(conn: sqlite3.Connection, session_id: str) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY seq", (session_id,)).fetchall()


def recent_messages(conn: sqlite3.Connection, session_id: str, limit: int, before_seq: int) -> list[sqlite3.Row]:
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE session_id = ? AND seq < ? AND status = 'complete' "
        "ORDER BY seq DESC LIMIT ?",
        (session_id, before_seq, limit),
    ).fetchall()
    return list(reversed(rows))
