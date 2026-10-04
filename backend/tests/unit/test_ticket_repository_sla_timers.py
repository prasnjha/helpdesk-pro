"""AC-05: repository-level timer-stop writes (sla-engine_spec.md).

Internal notes never stop the response timer; the first public agent reply
does. Reaching RESOLVED stops both timers if they are still running.
"""

from __future__ import annotations

from src.repository import ticket_repository
from src.types.clock import TestClock


def _create(engine, clock: TestClock, priority: str = "Critical"):
    return ticket_repository.create_ticket(
        engine,
        title="t",
        description="d",
        category="Billing",
        priority=priority,
        customer_id="C-1",
        now=clock.now(),
    )


def test_AC05_internal_note_does_not_stop_response_timer(engine, clock: TestClock) -> None:
    ticket = _create(engine, clock)
    clock.advance(5)
    ticket_repository.add_note(
        engine, ticket_id=ticket.id, author_id="AG-1", body="internal", now=clock.now()
    )
    reread = ticket_repository.get_by_id(engine, ticket.id)
    assert reread is not None
    assert reread.response_stopped_at is None


def test_AC05_first_agent_reply_stops_response_timer(engine, clock: TestClock) -> None:
    ticket = _create(engine, clock)
    clock.advance(5)
    ticket_repository.add_note(
        engine, ticket_id=ticket.id, author_id="AG-1", body="internal", now=clock.now()
    )
    clock.advance(15)
    _, updated = ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="AG-1",
        author_role="agent",
        body="hello",
        now=clock.now(),
    )
    assert updated.response_stopped_at == clock.now().isoformat()


def test_AC05_second_agent_reply_does_not_move_stopped_at(engine, clock: TestClock) -> None:
    ticket = _create(engine, clock)
    clock.advance(20)
    _, first = ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="AG-1",
        author_role="agent",
        body="hello",
        now=clock.now(),
    )
    first_stop = first.response_stopped_at
    clock.advance(30)
    _, second = ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="AG-1",
        author_role="agent",
        body="again",
        now=clock.now(),
    )
    assert second.response_stopped_at == first_stop


def test_AC05_customer_reply_does_not_stop_response_timer(engine, clock: TestClock) -> None:
    ticket = _create(engine, clock)
    clock.advance(10)
    _, updated = ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="C-1",
        author_role="customer",
        body="any update?",
        now=clock.now(),
    )
    assert updated.response_stopped_at is None


def test_AC05_resolved_stops_resolution_timer_and_response_if_still_running(
    engine, clock: TestClock
) -> None:
    ticket = ticket_repository.claim(
        engine, ticket_id=_create(engine, clock).id, actor_id="AG-1", version=1, now=clock.now()
    )
    clock.advance(200)
    resolved = ticket_repository.change_status(
        engine,
        ticket_id=ticket.id,
        actor_id="AG-1",
        to_status="RESOLVED",
        version=ticket.version,
        now=clock.now(),
    )
    assert resolved.resolution_stopped_at == clock.now().isoformat()
    assert resolved.response_stopped_at == clock.now().isoformat()


def test_AC05_resolved_does_not_move_an_already_stopped_response_timer(
    engine, clock: TestClock
) -> None:
    ticket = _create(engine, clock)
    clock.advance(5)
    _, replied = ticket_repository.add_reply(
        engine,
        ticket_id=ticket.id,
        author_id="AG-1",
        author_role="agent",
        body="hi",
        now=clock.now(),
    )
    response_stop = replied.response_stopped_at
    claimed = ticket_repository.claim(
        engine, ticket_id=ticket.id, actor_id="AG-1", version=replied.version, now=clock.now()
    )
    clock.advance(10)
    in_progress = ticket_repository.change_status(
        engine,
        ticket_id=ticket.id,
        actor_id="AG-1",
        to_status="PENDING_CUSTOMER",
        version=claimed.version,
        now=clock.now(),
    )
    clock.advance(20)
    resolved = ticket_repository.change_status(
        engine,
        ticket_id=ticket.id,
        actor_id="AG-1",
        to_status="RESOLVED",
        version=in_progress.version,
        now=clock.now(),
    )
    assert resolved.response_stopped_at == response_stop
