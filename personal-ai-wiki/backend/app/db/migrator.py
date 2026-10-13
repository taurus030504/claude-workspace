"""Versioned, forward-only schema migrations.

Safety rules (spec 15.10 "never automatically run migrations that could
destroy user data"):

* Migration files are ``NNNN_name.sql`` in ``app/db/migrations`` and are
  applied in order, each inside its own transaction.
* The SHA-256 of every applied file is recorded. If an applied file later
  changes, startup is refused instead of silently diverging.
* A database written by a newer app version (unknown migration numbers) is
  refused, so an old build can never "downgrade" it.
* Before applying anything to a database that already holds data, a verified
  backup is written to the backups directory.
* A migration containing the marker line ``-- paw:destructive`` (drops,
  table rebuilds that discard columns, ...) is never applied automatically.
  It runs only through ``python -m app.tools.migrate --allow-destructive``.
"""

from __future__ import annotations

import hashlib
import logging
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.core.timeutil import now_iso
from app.db.backup import backup_database
from app.db.connection import fts5_supports_trigram

log = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
DESTRUCTIVE_MARKER = "-- paw:destructive"
_FILE_RE = re.compile(r"^(\d{4})_([a-z0-9_]+)\.sql$")


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path
    sql: str
    checksum: str

    @property
    def destructive(self) -> bool:
        return DESTRUCTIVE_MARKER in self.sql


def discover(migrations_dir: Path = MIGRATIONS_DIR) -> list[Migration]:
    found: list[Migration] = []
    for path in sorted(migrations_dir.glob("*.sql")):
        m = _FILE_RE.match(path.name)
        if not m:
            raise MigrationError(f"bad migration file name: {path.name}")
        sql = path.read_text(encoding="utf-8")
        found.append(
            Migration(int(m.group(1)), m.group(2), path, sql, hashlib.sha256(sql.encode("utf-8")).hexdigest())
        )
    versions = [m.version for m in found]
    if len(set(versions)) != len(versions):
        raise MigrationError("duplicate migration version numbers")
    return found


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
               version     INTEGER PRIMARY KEY,
               name        TEXT NOT NULL,
               checksum    TEXT NOT NULL,
               applied_at  TEXT NOT NULL
           )"""
    )


def applied_versions(conn: sqlite3.Connection) -> dict[int, str]:
    _ensure_table(conn)
    return {r[0]: r[1] for r in conn.execute("SELECT version, checksum FROM schema_migrations")}


def _render(sql: str) -> str:
    tokenizer = "trigram" if fts5_supports_trigram() else "unicode61 remove_diacritics 2"
    return sql.replace("{{FTS_TOKENIZER}}", tokenizer)


def _has_user_data(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT IN ('schema_migrations')"
    ).fetchone()[0] > 0


def migrate(
    conn: sqlite3.Connection,
    backups_dir: Path | None,
    *,
    allow_destructive: bool = False,
    migrations_dir: Path = MIGRATIONS_DIR,
) -> list[int]:
    """Apply pending migrations. Returns the versions applied."""
    known = discover(migrations_dir)
    known_by_version = {m.version: m for m in known}
    applied = applied_versions(conn)

    unknown = sorted(v for v in applied if v not in known_by_version)
    if unknown:
        raise MigrationError(
            f"database has migrations {unknown} that this app version does not know; "
            "it was created by a newer version. Update the app instead of downgrading."
        )
    for version, checksum in applied.items():
        if known_by_version[version].checksum != checksum:
            raise MigrationError(
                f"migration {version:04d} was modified after it was applied. "
                "Restore the original file; never edit applied migrations."
            )

    pending = [m for m in known if m.version not in applied]
    if not pending:
        return []

    blocked = [m for m in pending if m.destructive]
    if blocked and not allow_destructive:
        names = ", ".join(m.path.name for m in blocked)
        raise MigrationError(
            f"pending migration(s) {names} may remove data and are not applied automatically. "
            "Back up your data, then run: python -m app.tools.migrate --allow-destructive"
        )

    if backups_dir is not None and _has_user_data(conn):
        target = backup_database(conn, backups_dir, label=f"pre-migration-{pending[0].version:04d}")
        log.info("database backed up to %s before migrating", target)

    done: list[int] = []
    for m in pending:
        script = (
            "BEGIN IMMEDIATE;\n"
            + _render(m.sql)
            + "\nINSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES "
            + f"({m.version}, '{m.name}', '{m.checksum}', '{now_iso()}');\nCOMMIT;"
        )
        try:
            conn.executescript(script)
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise MigrationError(f"migration {m.path.name} failed and was rolled back: {exc}") from exc
        log.info("applied migration %s", m.path.name)
        done.append(m.version)
    return done
