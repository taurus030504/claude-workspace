"""Restore the database from a backup file. Stop the backend first.

    python -m app.tools.restore <backup.db>
    python -m app.tools.restore --list

The current database is moved aside (never deleted) before the copy.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.config import get_settings
from app.db.backup import restore_database


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("backup", nargs="?", type=Path)
    parser.add_argument("--list", action="store_true", help="list available backups")
    args = parser.parse_args()
    settings = get_settings()

    if args.list or args.backup is None:
        for p in sorted(settings.backups_dir.glob("*.db")):
            print(f"{p}  {p.stat().st_size:,} bytes")
        return

    moved = restore_database(args.backup, settings.db_path)
    print(f"restored {args.backup} -> {settings.db_path}")
    if moved:
        print(f"previous database kept at {moved}")


if __name__ == "__main__":
    main()
