"""Manual migration runner.

    python -m app.tools.migrate                       # show status, apply safe migrations
    python -m app.tools.migrate --allow-destructive   # also apply migrations marked destructive

A backup is always written first when the database already has data.
"""

from __future__ import annotations

import argparse

from app.config import get_settings
from app.db.connection import connect
from app.db.migrator import applied_versions, discover, migrate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--allow-destructive", action="store_true")
    parser.add_argument("--status", action="store_true", help="only print status")
    args = parser.parse_args()

    settings = get_settings()
    settings.ensure_dirs()
    conn = connect(settings.db_path)
    try:
        applied = applied_versions(conn)
        for m in discover():
            state = "applied" if m.version in applied else "pending"
            flag = " (destructive)" if m.destructive else ""
            print(f"{m.version:04d} {m.name:<30} {state}{flag}")
        if args.status:
            return
        done = migrate(conn, settings.backups_dir, allow_destructive=args.allow_destructive)
        print("applied:", ", ".join(f"{v:04d}" for v in done) if done else "nothing to do")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
