"""Timeline event recording and retrieval.

Other services call :meth:`TimelineService.record` inside their own
transaction, so an event exists if and only if the change it describes was
committed. ``occurred_at`` is when the thing happened (for imported history,
the original time); ``recorded_at`` is always "now".
"""

from __future__ import annotations

import base64
import json
import sqlite3
from datetime import timedelta

from app.core.errors import ValidationError
from app.core.ids import new_id
from app.core.timeutil import normalize_iso, now_iso, parse_iso, utc_now
from app.repositories import timeline_repo
from app.schemas.timeline import TimelineEvent, TimelinePage


class EventType:
    WIKI_PAGE_CREATED = "wiki_page_created"
    WIKI_PAGE_UPDATED = "wiki_page_updated"
    WIKI_PAGE_DELETED = "wiki_page_deleted"
    WIKI_PAGE_RESTORED = "wiki_page_restored"
    # Reserved for later phases (listed so the vocabulary is defined in one place):
    MEMORY_CREATED = "memory_created"
    MEMORY_UPDATED = "memory_updated"
    PROJECT_CREATED = "project_created"
    PROJECT_STATUS_CHANGED = "project_status_changed"
    TASK_COMPLETED = "task_completed"
    DECISION_RECORDED = "decision_recorded"
    CONVERSATION_IMPORTED = "conversation_imported"


# Repeated saves of the same page within this window update one event
# instead of flooding the timeline with "modified" entries.
COALESCE_WINDOW = timedelta(minutes=10)


class TimelineService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def record(
        self,
        event_type: str,
        title: str,
        *,
        description: str = "",
        occurred_at: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        project_id: str | None = None,
        importance: int = 0,
        metadata: dict | None = None,
        coalesce: bool = False,
    ) -> str:
        now = now_iso()
        occurred = normalize_iso(occurred_at) if occurred_at else now
        if coalesce and source_type and source_id:
            last = timeline_repo.latest_for_source(self.conn, source_type, source_id)
            if (
                last is not None
                and last["event_type"] == event_type
                and utc_now() - parse_iso(last["recorded_at"]) <= COALESCE_WINDOW
            ):
                merged = json.loads(last["metadata"])
                merged.update(metadata or {})
                merged["edit_count"] = int(merged.get("edit_count", 1)) + 1
                timeline_repo.update_coalesced(
                    self.conn, last["event_id"], title=title, occurred_at=occurred, recorded_at=now, metadata=merged
                )
                return last["event_id"]
        event_id = new_id()
        timeline_repo.insert(
            self.conn,
            {
                "event_id": event_id,
                "event_type": event_type,
                "title": title,
                "description": description,
                "occurred_at": occurred,
                "recorded_at": now,
                "source_type": source_type,
                "source_id": source_id,
                "project_id": project_id,
                "importance": importance,
                "metadata": metadata or {},
            },
        )
        return event_id

    def query(
        self,
        *,
        start: str | None = None,
        end: str | None = None,
        event_types: list[str] | None = None,
        project_id: str | None = None,
        min_importance: int = 0,
        cursor: str | None = None,
        limit: int = 50,
    ) -> TimelinePage:
        before = _decode_cursor(cursor) if cursor else None
        rows = timeline_repo.query(
            self.conn,
            start=normalize_iso(start) if start else None,
            end=normalize_iso(end) if end else None,
            event_types=event_types,
            project_id=project_id,
            min_importance=min_importance,
            before=before,
            limit=limit + 1,
        )
        has_more = len(rows) > limit
        rows = rows[:limit]
        items = [_to_event(r) for r in rows]
        next_cursor = _encode_cursor(rows[-1]["occurred_at"], rows[-1]["event_id"]) if has_more else None
        return TimelinePage(items=items, next_cursor=next_cursor)


def _to_event(r: sqlite3.Row) -> TimelineEvent:
    return TimelineEvent(**{k: r[k] for k in r.keys() if k != "metadata"}, metadata=json.loads(r["metadata"]))


def _encode_cursor(occurred_at: str, event_id: str) -> str:
    return base64.urlsafe_b64encode(f"{occurred_at}|{event_id}".encode()).decode()


def _decode_cursor(cursor: str) -> tuple[str, str]:
    try:
        occurred_at, event_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        return occurred_at, event_id
    except Exception as exc:  # noqa: BLE001 - any malformed cursor is a client error
        raise ValidationError("invalid cursor") from exc
