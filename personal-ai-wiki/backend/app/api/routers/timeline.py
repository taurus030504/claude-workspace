from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import timeline_service
from app.schemas.timeline import TimelinePage
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/api/v1/timeline", tags=["timeline"])


@router.get("/events", response_model=TimelinePage)
def list_events(
    timeline: Annotated[TimelineService, Depends(timeline_service)],
    start: Annotated[str | None, Query(description="ISO-8601, inclusive (occurred_at)")] = None,
    end: Annotated[str | None, Query(description="ISO-8601, exclusive (occurred_at)")] = None,
    types: Annotated[str | None, Query(description="comma-separated event types")] = None,
    project_id: str | None = None,
    min_importance: Annotated[int, Query(ge=0, le=2)] = 0,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
):
    event_types = [t.strip() for t in types.split(",") if t.strip()] if types else None
    return timeline.query(
        start=start, end=end, event_types=event_types, project_id=project_id,
        min_importance=min_importance, cursor=cursor, limit=limit,
    )
