import shutil

import pytest

from app.db.backup import backup_database, restore_database, verify_database
from app.db.connection import connect
from app.db.migrator import MIGRATIONS_DIR, MigrationError, applied_versions, migrate


@pytest.fixture
def mig_dir(tmp_path):
    d = tmp_path / "migrations"
    shutil.copytree(MIGRATIONS_DIR, d)
    return d


def test_fresh_database_gets_all_tables_and_trigram_index(tmp_path):
    conn = connect(tmp_path / "a.db")
    assert migrate(conn, tmp_path / "backups") == [1]
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for t in ("wiki_pages", "wiki_revisions", "wiki_chunks", "tags", "entity_tags", "chat_sessions",
              "chat_messages", "timeline_events", "source_references", "app_settings", "search_index"):
        assert t in tables
    sql = conn.execute("SELECT sql FROM sqlite_master WHERE name='search_index'").fetchone()[0]
    assert "trigram" in sql
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    # no backup for an empty database
    assert not list((tmp_path / "backups").glob("*.db"))


def test_second_run_is_a_no_op(tmp_path):
    conn = connect(tmp_path / "a.db")
    migrate(conn, None)
    assert migrate(conn, None) == []


def test_modified_applied_migration_is_refused(tmp_path, mig_dir):
    conn = connect(tmp_path / "a.db")
    migrate(conn, None, migrations_dir=mig_dir)
    f = mig_dir / "0001_initial.sql"
    f.write_text(f.read_text(encoding="utf-8") + "\n-- edited", encoding="utf-8")
    with pytest.raises(MigrationError, match="modified"):
        migrate(conn, None, migrations_dir=mig_dir)


def test_database_from_newer_version_is_refused(tmp_path):
    conn = connect(tmp_path / "a.db")
    migrate(conn, None)
    conn.execute("INSERT INTO schema_migrations VALUES (999, 'future', 'x', '2030-01-01T00:00:00.000Z')")
    with pytest.raises(MigrationError, match="newer version"):
        migrate(conn, None)


def test_pending_migration_backs_up_existing_data_first(tmp_path, mig_dir):
    conn = connect(tmp_path / "a.db")
    migrate(conn, None, migrations_dir=mig_dir)
    conn.execute("INSERT INTO app_settings VALUES ('k', '1', 'now')")
    (mig_dir / "0002_add_col.sql").write_text("ALTER TABLE app_settings ADD COLUMN note TEXT;", encoding="utf-8")
    assert migrate(conn, tmp_path / "backups", migrations_dir=mig_dir) == [2]
    backups = list((tmp_path / "backups").glob("paw-pre-migration-0002-*.db"))
    assert len(backups) == 1
    restored = connect(backups[0])
    assert restored.execute("SELECT value FROM app_settings WHERE key='k'").fetchone()[0] == "1"


def test_destructive_migration_requires_explicit_flag(tmp_path, mig_dir):
    conn = connect(tmp_path / "a.db")
    migrate(conn, None, migrations_dir=mig_dir)
    (mig_dir / "0002_drop.sql").write_text("-- paw:destructive\nDROP TABLE app_settings;", encoding="utf-8")
    with pytest.raises(MigrationError, match="not applied automatically"):
        migrate(conn, None, migrations_dir=mig_dir)
    assert 2 not in applied_versions(conn)
    assert migrate(conn, tmp_path / "b", migrations_dir=mig_dir, allow_destructive=True) == [2]


def test_failed_migration_rolls_back(tmp_path, mig_dir):
    conn = connect(tmp_path / "a.db")
    migrate(conn, None, migrations_dir=mig_dir)
    (mig_dir / "0002_bad.sql").write_text(
        "CREATE TABLE half_done (x INTEGER);\nTHIS IS NOT SQL;", encoding="utf-8"
    )
    with pytest.raises(MigrationError, match="rolled back"):
        migrate(conn, None, migrations_dir=mig_dir)
    assert conn.execute("SELECT count(*) FROM sqlite_master WHERE name='half_done'").fetchone()[0] == 0
    assert 2 not in applied_versions(conn)


def test_backup_and_restore_round_trip(tmp_path):
    db = tmp_path / "live.db"
    conn = connect(db)
    migrate(conn, None)
    conn.execute("INSERT INTO app_settings VALUES ('v', '\"before\"', 'now')")
    backup = backup_database(conn, tmp_path / "backups")
    verify_database(backup)
    conn.execute("UPDATE app_settings SET value = '\"after\"' WHERE key = 'v'")
    conn.close()

    moved = restore_database(backup, db)
    assert moved is not None and moved.exists()  # old database kept, not deleted
    again = connect(db)
    assert again.execute("SELECT value FROM app_settings WHERE key='v'").fetchone()[0] == '"before"'
