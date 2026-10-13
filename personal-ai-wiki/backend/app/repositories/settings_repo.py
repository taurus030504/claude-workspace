"""User-changeable settings stored as JSON values."""

from __future__ import annotations

import json
import sqlite3
from typing import Any


def get_all(conn: sqlite3.Connection) -> dict[str, Any]:
    return {r[0]: json.loads(r[1]) for r in conn.execute("SELECT key, value FROM app_settings")}


def set_value(conn: sqlite3.Connection, key: str, value: Any, now: str) -> None:
    conn.execute(
        "INSERT INTO app_settings (key, value, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
        (key, json.dumps(value, ensure_ascii=False), now),
    )
