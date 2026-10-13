"""Online backup and offline restore of the SQLite database.

Backups use SQLite's backup API, which produces a consistent copy even while
the app is running. Restore never deletes the current database: it is moved
aside to ``<name>.before-restore-<timestamp>.db`` first.
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_database(conn: sqlite3.Connection, backups_dir: Path, label: str = "manual") -> Path:
    backups_dir.mkdir(parents=True, exist_ok=True)
    target = backups_dir / f"paw-{label}-{_stamp()}.db"
    suffix = 1
    while target.exists():
        target = backups_dir / f"paw-{label}-{_stamp()}-{suffix}.db"
        suffix += 1
    dest = sqlite3.connect(str(target))
    try:
        conn.backup(dest)
    finally:
        dest.close()
    verify_database(target)
    return target


def verify_database(path: Path) -> None:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        conn.close()
    if result != "ok":
        raise RuntimeError(f"integrity check failed for {path}: {result}")


def restore_database(backup_file: Path, db_path: Path) -> Path | None:
    """Replace ``db_path`` with ``backup_file``. The backend must be stopped.

    Returns the path the previous database was moved to (None if there was none).
    """
    verify_database(backup_file)
    moved_to: Path | None = None
    if db_path.exists():
        moved_to = db_path.with_name(f"{db_path.stem}.before-restore-{_stamp()}.db")
        db_path.rename(moved_to)
        for ext in ("-wal", "-shm"):
            side = db_path.with_name(db_path.name + ext)
            if side.exists():
                side.rename(moved_to.with_name(moved_to.name + ext))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_file, db_path)
    return moved_to
