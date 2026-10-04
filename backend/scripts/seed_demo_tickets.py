"""Seed ~15 demo tickets across all five lifecycle states, including a
Billing breach escalated to tier 2 (E6-S4, BRD A-16, M8).

Goes through the real service layer (create, claim, status, reply) with a
deterministic `TestClock` so every row respects the same invariants the app
enforces at runtime (append-only history, version bumps, routing, the SLA
breach-and-escalate transaction). This is a standalone script, not a
migration: it runs once against the real `helpdesk.db`, never against the
per-test in-memory database (tests apply only `src/repository/migrations/`,
never this script), so it cannot change any existing test's expectations.

Usage (from `backend/`): `uv run python scripts/seed_demo_tickets.py`
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import Engine, create_engine, text  # noqa: E402

from src.config.settings import get_settings  # noqa: E402
from src.repository.db import run_migrations  # noqa: E402
from src.service.sla_service import get_snapshot_for_agent  # noqa: E402
from src.service.ticket_service import (  # noqa: E402
    add_reply,
    change_ticket_status,
    claim_ticket,
    create_ticket,
)
from src.types.clock import TestClock  # noqa: E402

DEMO_MARKER = "[DEMO]"

CUSTOMER_1 = "C-1"
CUSTOMER_2 = "C-2"
AGENT_1 = "AG-1"
AGENT_2 = "AG-2"


@dataclass(frozen=True)
class DemoTicket:
    title: str
    description: str
    category: str
    priority: str
    customer_id: str


# 14 tickets walked through a realistic lifecycle below, plus one more
# (the 15th) created already-breached further down — one per state is not
# enough on its own to reach "about 15", so several states get more than one.
OPEN_TICKETS = [
    DemoTicket(
        f"{DEMO_MARKER} Invoice shows duplicate charge",
        "Billed twice this month.",
        "Billing",
        "High",
        CUSTOMER_1,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Cannot download last statement",
        "PDF link returns an error.",
        "Billing",
        "Low",
        CUSTOMER_2,
    ),
    DemoTicket(
        f"{DEMO_MARKER} API key stopped working",
        "Requests return 401 since this morning.",
        "Technical",
        "Critical",
        CUSTOMER_1,
    ),
]

IN_PROGRESS_TICKETS = [
    DemoTicket(
        f"{DEMO_MARKER} Integration webhook retries failing",
        "Webhook retries time out.",
        "Technical",
        "High",
        CUSTOMER_2,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Update billing address",
        "Need the address on file updated.",
        "Account",
        "Medium",
        CUSTOMER_1,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Add a second admin seat",
        "Need another admin on the account.",
        "Account",
        "Low",
        CUSTOMER_2,
    ),
]

PENDING_CUSTOMER_TICKETS = [
    DemoTicket(
        f"{DEMO_MARKER} Refund request for cancelled plan",
        "Cancelled but still charged.",
        "Billing",
        "Medium",
        CUSTOMER_1,
    ),
    DemoTicket(
        f"{DEMO_MARKER} SSO login redirect loop",
        "Login redirects back to the IdP.",
        "Technical",
        "High",
        CUSTOMER_2,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Merge two customer accounts",
        "Two accounts need to become one.",
        "Account",
        "Low",
        CUSTOMER_1,
    ),
]

RESOLVED_TICKETS = [
    DemoTicket(
        f"{DEMO_MARKER} Password reset email never arrives",
        "Reset email never arrives.",
        "Account",
        "Medium",
        CUSTOMER_2,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Export is missing a column",
        "CSV export is missing a column.",
        "Technical",
        "Low",
        CUSTOMER_1,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Proration looks wrong on upgrade",
        "Proration on upgrade looks wrong.",
        "Billing",
        "Medium",
        CUSTOMER_2,
    ),
]

CLOSED_TICKETS = [
    DemoTicket(
        f"{DEMO_MARKER} Dashboard chart not loading",
        "Resolved and confirmed by customer.",
        "Technical",
        "Low",
        CUSTOMER_1,
    ),
    DemoTicket(
        f"{DEMO_MARKER} Duplicate ticket, closed as dup",
        "Duplicate of another ticket.",
        "Account",
        "Low",
        CUSTOMER_2,
    ),
]

# The 15th ticket: a Critical Billing ticket old enough to breach its
# response timer (SLA policy v1: Critical = 15 response minutes), so that
# reading its SLA snapshot escalates it to Billing Tier 2 in the same
# transaction the running app would use (escalation_spec.md, AC-06).
BREACH_TICKET = DemoTicket(
    f"{DEMO_MARKER} Critical: payment processor down",
    "Payments are failing for all customers.",
    "Billing",
    "Critical",
    CUSTOMER_1,
)


def _already_seeded(engine: Engine) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT COUNT(*) FROM tickets WHERE title LIKE :marker"),
            {"marker": f"{DEMO_MARKER}%"},
        ).scalar_one()
    return bool(row)


def seed(engine: Engine, clock: TestClock) -> int:
    """Create the demo tickets and walk each one to its target state.
    Returns the number of tickets created. Idempotent: a second run is a
    no-op if demo tickets already exist.
    """
    if _already_seeded(engine):
        return 0

    created = 0

    for demo in OPEN_TICKETS:
        create_ticket(
            engine,
            clock,
            title=demo.title,
            description=demo.description,
            category=demo.category,
            priority=demo.priority,
            customer_id=demo.customer_id,
        )
        clock.advance(5)
        created += 1

    for demo in IN_PROGRESS_TICKETS:
        ticket = create_ticket(
            engine,
            clock,
            title=demo.title,
            description=demo.description,
            category=demo.category,
            priority=demo.priority,
            customer_id=demo.customer_id,
        )
        clock.advance(5)
        claim_ticket(engine, clock, ticket_id=ticket.id, actor_id=AGENT_1, version=ticket.version)
        clock.advance(5)
        created += 1

    for demo in PENDING_CUSTOMER_TICKETS:
        ticket = create_ticket(
            engine,
            clock,
            title=demo.title,
            description=demo.description,
            category=demo.category,
            priority=demo.priority,
            customer_id=demo.customer_id,
        )
        clock.advance(5)
        claimed = claim_ticket(
            engine, clock, ticket_id=ticket.id, actor_id=AGENT_2, version=ticket.version
        )
        clock.advance(5)
        change_ticket_status(
            engine,
            clock,
            ticket_id=ticket.id,
            actor_id=AGENT_2,
            to_status="PENDING_CUSTOMER",
            version=claimed.version,
        )
        clock.advance(5)
        created += 1

    for demo in RESOLVED_TICKETS:
        ticket = create_ticket(
            engine,
            clock,
            title=demo.title,
            description=demo.description,
            category=demo.category,
            priority=demo.priority,
            customer_id=demo.customer_id,
        )
        clock.advance(5)
        claimed = claim_ticket(
            engine, clock, ticket_id=ticket.id, actor_id=AGENT_1, version=ticket.version
        )
        clock.advance(5)
        change_ticket_status(
            engine,
            clock,
            ticket_id=ticket.id,
            actor_id=AGENT_1,
            to_status="RESOLVED",
            version=claimed.version,
        )
        clock.advance(5)
        created += 1

    for demo in CLOSED_TICKETS:
        ticket = create_ticket(
            engine,
            clock,
            title=demo.title,
            description=demo.description,
            category=demo.category,
            priority=demo.priority,
            customer_id=demo.customer_id,
        )
        clock.advance(5)
        claimed = claim_ticket(
            engine, clock, ticket_id=ticket.id, actor_id=AGENT_1, version=ticket.version
        )
        clock.advance(5)
        resolved = change_ticket_status(
            engine,
            clock,
            ticket_id=ticket.id,
            actor_id=AGENT_1,
            to_status="RESOLVED",
            version=claimed.version,
        )
        clock.advance(5)
        change_ticket_status(
            engine,
            clock,
            ticket_id=ticket.id,
            actor_id=AGENT_1,
            to_status="CLOSED",
            version=resolved.version,
        )
        clock.advance(5)
        created += 1

    breach = create_ticket(
        engine,
        clock,
        title=BREACH_TICKET.title,
        description=BREACH_TICKET.description,
        category=BREACH_TICKET.category,
        priority=BREACH_TICKET.priority,
        customer_id=BREACH_TICKET.customer_id,
    )
    # Critical response target is 15 minutes (sla_policy v1); wait well past
    # it, then read the SLA snapshot the way the app does — the same read
    # evaluates the breach and escalates to Billing Tier 2 in one
    # transaction (api-contracts.md "SLA read", escalation_spec.md).
    clock.advance(30)
    get_snapshot_for_agent(engine, clock, breach.id)
    # A customer reply after escalation shows the ticket is still active,
    # not abandoned (api-contracts.md "Lifecycle, claim, reassign").
    add_reply(
        engine,
        clock,
        ticket_id=breach.id,
        author_id=breach.customer_id,
        author_role="customer",
        body="Any update? This is blocking our customers too.",
    )
    created += 1

    return created


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    run_migrations(engine, settings.migrations_dir)
    clock = TestClock()
    count = seed(engine, clock)
    if count:
        print(f"Seeded {count} demo tickets.")
    else:
        print("Demo tickets already present; nothing to do.")


if __name__ == "__main__":
    main()
