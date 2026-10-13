"""All timestamps are stored as UTC ISO-8601 strings with a trailing ``Z``.

The fixed format (millisecond precision) keeps lexical order equal to time
order, so SQLite can sort and range-filter the TEXT columns directly.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError("naive datetime; attach a timezone before storing")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def now_iso() -> str:
    return to_iso(utc_now())


def parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def normalize_iso(value: str) -> str:
    """Accept any ISO-8601 input (with offset) and return the canonical UTC form."""
    return to_iso(parse_iso(value))
