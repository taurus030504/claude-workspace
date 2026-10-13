from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class TimelineEvent(BaseModel):
    event_id: str
    event_type: str
    title: str
    description: str
    occurred_at: str
    recorded_at: str
    source_type: str | None
    source_id: str | None
    project_id: str | None
    importance: int
    metadata: dict[str, Any]


class TimelinePage(BaseModel):
    items: list[TimelineEvent]
    next_cursor: str | None
