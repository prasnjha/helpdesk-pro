from __future__ import annotations

from src.repository import assignment_repository, ticket_repository
from src.types.clock import TestClock


def test_AC03_list_for_ticket_returns_rows_in_insertion_order(engine) -> None:
    clock = TestClock()
    ticket = ticket_repository.create_ticket(
        engine,
        title="t",
        description="d",
        category="Billing",
        priority="High",
        customer_id="C-1",
        now=clock.now(),
    )
    ticket_repository.claim(
        engine, ticket_id=ticket.id, actor_id="AG-1", version=1, now=clock.now()
    )
    ticket_repository.reassign(
        engine, ticket_id=ticket.id, actor_id="AG-2", assignee_id="AG-2", version=2, now=clock.now()
    )

    rows = assignment_repository.list_for_ticket(engine, ticket.id)
    assert [(r.from_user_id, r.to_user_id) for r in rows] == [(None, "AG-1"), ("AG-1", "AG-2")]
