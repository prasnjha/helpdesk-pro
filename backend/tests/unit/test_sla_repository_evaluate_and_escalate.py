"""AC-05, AC-06: the one SLA domain function that runs on every ticket read
through `GET /api/tickets/{id}/sla` (escalation_spec.md: "no scheduler").
"""

from __future__ import annotations

from src.repository import sla_event_repository, sla_repository, ticket_repository
from src.types.clock import TestClock


def _billing_critical_ticket(engine, clock: TestClock):
    return ticket_repository.create_ticket(
        engine,
        title="t",
        description="d",
        category="Billing",
        priority="Critical",
        customer_id="C-1",
        now=clock.now(),
    )


def test_AC06_response_breach_escalates_to_tier_2(engine) -> None:
    clock = TestClock()
    ticket = _billing_critical_ticket(engine, clock)
    clock.advance(15)  # Critical response target is 15 minutes
    snapshot = sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    assert snapshot is not None
    assert snapshot.response.state == "BREACHED"
    updated = ticket_repository.get_by_id(engine, ticket.id)
    assert updated is not None
    assert updated.escalated is True
    assert updated.status == "OPEN"
    assert updated.queue.slug == "billing-tier-2"


def test_AC06_repeat_read_after_breach_writes_no_new_sla_event(engine) -> None:
    clock = TestClock()
    ticket = _billing_critical_ticket(engine, clock)
    clock.advance(15)
    sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    with engine.connect() as conn:
        first_count = len(sla_event_repository.list_for_ticket(conn, ticket.id))
    clock.advance(5)
    sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    with engine.connect() as conn:
        second_count = len(sla_event_repository.list_for_ticket(conn, ticket.id))
    assert second_count == first_count


def test_AC06_both_timers_breach_escalates_only_once(engine) -> None:
    clock = TestClock()
    ticket = _billing_critical_ticket(engine, clock)
    clock.advance(15)
    sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    clock.advance(240)  # now past the 240-minute resolution target too
    sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    with engine.connect() as conn:
        events = sla_event_repository.list_for_ticket(conn, ticket.id)
    assert len([e for e in events if e.event == "BREACHED_RESPONSE"]) == 1
    assert len([e for e in events if e.event == "BREACHED_RESOLUTION"]) == 1
    assert len([e for e in events if e.event == "ESCALATED"]) == 1
    updated = ticket_repository.get_by_id(engine, ticket.id)
    assert updated is not None
    assert updated.queue.slug == "billing-tier-2"


def test_AC06_public_reply_before_deadline_prevents_a_breach(engine) -> None:
    clock = TestClock()
    ticket = _billing_critical_ticket(engine, clock)
    clock.advance(5)
    ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="AG-1",
        author_role="agent",
        body="on it",
        now=clock.now(),
    )
    clock.advance(30)
    snapshot = sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    assert snapshot is not None
    assert snapshot.response.state == "ON_TRACK"
    updated = ticket_repository.get_by_id(engine, ticket.id)
    assert updated is not None
    assert updated.escalated is False


def test_AC06_escalated_stays_true_after_a_customer_reply(engine) -> None:
    clock = TestClock()
    ticket = _billing_critical_ticket(engine, clock)
    clock.advance(15)
    sla_repository.evaluate_and_escalate(engine, ticket_id=ticket.id, now=clock.now())
    ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="C-1",
        author_role="customer",
        body="any update?",
        now=clock.now(),
    )
    updated = ticket_repository.get_by_id(engine, ticket.id)
    assert updated is not None
    assert updated.escalated is True


def test_AC06_closed_ticket_is_never_written_to_even_by_a_read(engine) -> None:
    clock = TestClock()
    ticket = ticket_repository.claim(
        engine,
        ticket_id=_billing_critical_ticket(engine, clock).id,
        actor_id="AG-1",
        version=1,
        now=clock.now(),
    )
    clock.advance(15)  # breach the response timer before resolving
    resolved = ticket_repository.change_status(
        engine,
        ticket_id=ticket.id,
        actor_id="AG-1",
        to_status="RESOLVED",
        version=ticket.version,
        now=clock.now(),
    )
    closed = ticket_repository.change_status(
        engine,
        ticket_id=ticket.id,
        actor_id="AG-1",
        to_status="CLOSED",
        version=resolved.version,
        now=clock.now(),
    )
    with engine.connect() as conn:
        before = len(sla_event_repository.list_for_ticket(conn, closed.id))
    clock.advance(1000)
    sla_repository.evaluate_and_escalate(engine, ticket_id=closed.id, now=clock.now())
    with engine.connect() as conn:
        after = len(sla_event_repository.list_for_ticket(conn, closed.id))
    assert after == before == 0
    updated = ticket_repository.get_by_id(engine, closed.id)
    assert updated is not None
    assert updated.escalated is False


def test_AC06_unknown_ticket_returns_none(engine) -> None:
    clock = TestClock()
    result = sla_repository.evaluate_and_escalate(engine, ticket_id="HD-999999", now=clock.now())
    assert result is None
