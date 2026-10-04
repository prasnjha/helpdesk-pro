"""AC-06: the escalate write (escalation_spec.md). One TicketHistory row with
event ESCALATED, actor system; status is unchanged; queue moves to tier 2.
"""

from __future__ import annotations

from src.repository import team_repository, ticket_repository
from src.types.clock import TestClock


def test_AC06_escalate_moves_queue_and_sets_escalated_flag(engine) -> None:
    clock = TestClock()
    ticket = ticket_repository.create_ticket(
        engine,
        title="t",
        description="d",
        category="Billing",
        priority="Critical",
        customer_id="C-1",
        now=clock.now(),
    )
    with engine.begin() as conn:
        tier2_id = team_repository.get_id_by_slug(conn, "billing-tier-2")
        assert tier2_id is not None
        updated = ticket_repository.escalate(
            conn, ticket_id=ticket.id, to_queue_id=tier2_id, now=clock.now()
        )
    assert updated.escalated is True
    assert updated.status == "OPEN"
    assert updated.queue.slug == "billing-tier-2"
    history = ticket_repository.list_history_for(engine, ticket.id)
    escalated_rows = [h for h in history if h.event == "ESCALATED"]
    assert len(escalated_rows) == 1
    assert escalated_rows[0].actor_id == "system"
