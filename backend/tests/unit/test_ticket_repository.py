from __future__ import annotations

from sqlalchemy import text

from src.repository import ticket_repository
from src.types.clock import TestClock


def test_E2S1_sequential_creates_get_HD_000001_and_000002(engine) -> None:
    clock = TestClock()
    t1 = ticket_repository.create_ticket(
        engine,
        title="a",
        description="b",
        category="Billing",
        priority="High",
        customer_id="C-1",
        now=clock.now(),
    )
    t2 = ticket_repository.create_ticket(
        engine,
        title="a2",
        description="b2",
        category="Billing",
        priority="High",
        customer_id="C-1",
        now=clock.now(),
    )
    assert t1.id == "HD-000001"
    assert t2.id == "HD-000002"
    assert t1.id != t2.id


def test_E2S1_stores_active_policy_version_for_priority(engine) -> None:
    clock = TestClock()
    with engine.connect() as conn:
        expected = conn.execute(
            text("SELECT id FROM sla_policy WHERE priority = 'High'")
        ).scalar_one()
    ticket = ticket_repository.create_ticket(
        engine,
        title="a",
        description="b",
        category="Billing",
        priority="High",
        customer_id="C-1",
        now=clock.now(),
    )
    assert ticket.sla_policy_version_id == expected


def test_E2S1_failed_insert_leaves_no_partial_row(engine) -> None:
    clock = TestClock()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM routing_rules WHERE category = 'Billing'"))
    try:
        ticket_repository.create_ticket(
            engine,
            title="a",
            description="b",
            category="Billing",
            priority="High",
            customer_id="C-1",
            now=clock.now(),
        )
    except Exception:
        pass
    assert ticket_repository.count_tickets(engine) == 0
