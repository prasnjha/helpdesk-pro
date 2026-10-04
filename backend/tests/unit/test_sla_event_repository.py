"""AC-06: SlaEvent repository (escalation_spec.md). Append-only: insert and
read only, no update or delete.
"""

from __future__ import annotations

import inspect

from src.repository import sla_event_repository

_FORBIDDEN_NAME_FRAGMENTS = ("update", "delete", "remove", "edit", "modify")


def test_AC06_sla_event_repository_has_no_update_or_delete_method() -> None:
    functions = inspect.getmembers(sla_event_repository, inspect.isfunction)
    names = [name for name, _ in functions if not name.startswith("_")]
    assert names
    for name in names:
        lowered = name.lower()
        assert not any(fragment in lowered for fragment in _FORBIDDEN_NAME_FRAGMENTS)


def _ticket_id(engine) -> str:
    from src.repository import ticket_repository
    from src.types.clock import TestClock

    return ticket_repository.create_ticket(
        engine,
        title="t",
        description="d",
        category="Billing",
        priority="Critical",
        customer_id="C-1",
        now=TestClock().now(),
    ).id


def test_AC06_insert_and_list_round_trip(engine) -> None:
    ticket_id = _ticket_id(engine)
    with engine.begin() as conn:
        sla_event_repository.insert(
            conn,
            ticket_id=ticket_id,
            event="BREACHED_RESPONSE",
            timer="response",
            breached_at="2026-01-01T00:15:00+00:00",
            created_at="2026-01-01T00:20:00+00:00",
        )
    with engine.connect() as conn:
        events = sla_event_repository.list_for_ticket(conn, ticket_id)
    assert len(events) == 1
    assert events[0].event == "BREACHED_RESPONSE"
    assert events[0].timer == "response"


def test_AC06_has_breach_false_until_recorded(engine) -> None:
    ticket_id = _ticket_id(engine)
    with engine.connect() as conn:
        assert sla_event_repository.has_breach(conn, ticket_id, "response") is False
    with engine.begin() as conn:
        sla_event_repository.insert(
            conn,
            ticket_id=ticket_id,
            event="BREACHED_RESPONSE",
            timer="response",
            breached_at="2026-01-01T00:15:00+00:00",
            created_at="2026-01-01T00:20:00+00:00",
        )
    with engine.connect() as conn:
        assert sla_event_repository.has_breach(conn, ticket_id, "response") is True
        assert sla_event_repository.has_breach(conn, ticket_id, "resolution") is False


def test_AC06_has_escalation_false_until_recorded(engine) -> None:
    ticket_id = _ticket_id(engine)
    with engine.connect() as conn:
        assert sla_event_repository.has_escalation(conn, ticket_id) is False
    with engine.begin() as conn:
        sla_event_repository.insert(
            conn,
            ticket_id=ticket_id,
            event="ESCALATED",
            timer=None,
            breached_at=None,
            created_at="2026-01-01T00:20:00+00:00",
        )
    with engine.connect() as conn:
        assert sla_event_repository.has_escalation(conn, ticket_id) is True
