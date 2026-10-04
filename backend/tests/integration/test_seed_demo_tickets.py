"""E6-S4: the demo seed script reaches all five lifecycle states and leaves
at least one Billing ticket escalated to Billing Tier 2 after a breach.
"""

from __future__ import annotations

from scripts.seed_demo_tickets import seed
from src.service.agent_queue_service import list_queue_tickets
from src.types.clock import TestClock

_QUEUES = [
    "billing",
    "technical",
    "account",
    "billing-tier-2",
    "technical-tier-2",
    "account-tier-2",
]


def _all_tickets(engine, clock: TestClock):
    rows = []
    for slug in _QUEUES:
        rows.extend(
            list_queue_tickets(
                engine, clock, queue_slug=slug, priority=None, status=None, escalated=None
            )
        )
    return rows


def test_E6S4_seed_creates_tickets_in_all_five_lifecycle_states(engine) -> None:
    clock = TestClock()
    created = seed(engine, clock)
    assert created == 15

    statuses = {row.ticket.status for row in _all_tickets(engine, clock)}
    assert {"OPEN", "IN_PROGRESS", "PENDING_CUSTOMER", "RESOLVED", "CLOSED"} <= statuses


def test_E6S4_seed_leaves_one_billing_ticket_escalated_to_tier_2_after_a_breach(engine) -> None:
    clock = TestClock()
    seed(engine, clock)

    tier_2_tickets = list_queue_tickets(
        engine, clock, queue_slug="billing-tier-2", priority=None, status=None, escalated=None
    )
    assert len(tier_2_tickets) >= 1
    assert all(row.ticket.escalated for row in tier_2_tickets)


def test_E6S4_seed_is_idempotent(engine) -> None:
    clock = TestClock()
    first = seed(engine, clock)
    second = seed(engine, TestClock())
    assert first == 15
    assert second == 0
