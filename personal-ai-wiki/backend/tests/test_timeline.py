from app.db.connection import transaction
from app.services.timeline_service import TimelineService


def test_occurred_at_is_kept_separate_from_recorded_at(conn):
    svc = TimelineService(conn)
    with transaction(conn):
        svc.record("conversation_imported", "과거 대화", occurred_at="2025-03-01T09:00:00+09:00",
                   source_type="chat_session", source_id="s1")
    e = svc.query().items[0]
    assert e.occurred_at == "2025-03-01T00:00:00.000Z"  # stored as UTC
    assert e.recorded_at > e.occurred_at                # recorded now, not backdated


def test_filters_and_cursor_pagination(conn):
    svc = TimelineService(conn)
    with transaction(conn):
        for day in range(1, 21):
            svc.record(
                "task_completed" if day % 2 else "decision_recorded",
                f"event {day}",
                occurred_at=f"2026-09-{day:02d}T12:00:00Z",
                project_id="p1" if day <= 10 else "p2",
                importance=2 if day == 5 else 0,
            )

    page1 = svc.query(limit=8)
    page2 = svc.query(limit=8, cursor=page1.next_cursor)
    page3 = svc.query(limit=8, cursor=page2.next_cursor)
    titles = [e.title for p in (page1, page2, page3) for e in p.items]
    assert titles == [f"event {d}" for d in range(20, 0, -1)]
    assert page3.next_cursor is None

    sept_early = svc.query(start="2026-09-01T00:00:00Z", end="2026-09-04T00:00:00Z")
    assert [e.title for e in sept_early.items] == ["event 3", "event 2", "event 1"]
    assert all(e.event_type == "decision_recorded" for e in svc.query(event_types=["decision_recorded"]).items)
    assert len(svc.query(project_id="p2", limit=100).items) == 10
    assert [e.title for e in svc.query(min_importance=2).items] == ["event 5"]


def test_api_rejects_bad_cursor(client):
    r = client.get("/api/v1/timeline/events", params={"cursor": "%%%"})
    assert r.status_code == 422
