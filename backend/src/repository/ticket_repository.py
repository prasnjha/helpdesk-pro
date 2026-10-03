"""Ticket writes. Routing and the ticket insert share one transaction (ASM-S7).

Ticket history is append-only: insert and read only, no update or delete.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine, text

from src.domain.routing import resolve_queue_id
from src.repository import routing_repository, sla_policy_repository, team_repository
from src.types.errors import RoutingRuleMissingError
from src.types.models import TicketRecord, TicketSummary


def create_ticket(
    engine: Engine,
    *,
    title: str,
    description: str,
    category: str,
    priority: str,
    customer_id: str,
    now: datetime,
) -> TicketRecord:
    """Route and insert a ticket in one transaction. No partial row on failure."""
    with engine.begin() as conn:
        rules = routing_repository.get_all_rules(conn)
        try:
            queue_id = resolve_queue_id(category, rules)
        except RoutingRuleMissingError:
            # Raising here aborts the `with` block, rolling back; nothing is
            # written when there is no rule for the category.
            raise

        policy_version_id = sla_policy_repository.get_active_version_id(conn, priority)
        if policy_version_id is None:
            raise RoutingRuleMissingError(f"No SLA policy for priority '{priority}'")

        created_at = now.isoformat()
        result = conn.execute(
            text(
                "INSERT INTO tickets "
                "(id, title, description, category, priority, status, queue_id, "
                " customer_id, assignee_id, escalated, sla_policy_version_id, "
                " version, created_at, updated_at) "
                "VALUES (NULL, :title, :description, :category, :priority, 'OPEN', "
                " :queue_id, :customer_id, NULL, 0, :policy_version_id, 1, "
                " :created_at, :created_at)"
            ),
            {
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "queue_id": queue_id,
                "customer_id": customer_id,
                "policy_version_id": policy_version_id,
                "created_at": created_at,
            },
        )
        seq = result.lastrowid
        ticket_id = f"HD-{seq:06d}"
        conn.execute(
            text("UPDATE tickets SET id = :id WHERE seq = :seq"),
            {"id": ticket_id, "seq": seq},
        )
        conn.execute(
            text(
                "INSERT INTO ticket_history "
                "(ticket_id, event, from_state, to_state, actor_id, correlation_id, created_at) "
                "VALUES (:ticket_id, 'ROUTED', NULL, 'OPEN', 'system', NULL, :created_at)"
            ),
            {"ticket_id": ticket_id, "created_at": created_at},
        )
        queue = team_repository.get_by_id(conn, queue_id)
        assert queue is not None

    return TicketRecord(
        id=ticket_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status="OPEN",
        queue=queue,
        customer_id=customer_id,
        assignee_id=None,
        escalated=False,
        sla_policy_version_id=policy_version_id,
        version=1,
        created_at=created_at,
        updated_at=created_at,
    )


def list_for_customer(engine: Engine, customer_id: str) -> list[TicketSummary]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT id, title, status, priority, category, updated_at "
                "FROM tickets WHERE customer_id = :customer_id ORDER BY seq"
            ),
            {"customer_id": customer_id},
        ).mappings().all()
        return [TicketSummary(**row) for row in rows]


def count_tickets(engine: Engine) -> int:
    with engine.connect() as conn:
        return int(conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one())


def history_events_for(engine: Engine, ticket_id: str) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT event FROM ticket_history WHERE ticket_id = :id"),
            {"id": ticket_id},
        ).all()
        return [row[0] for row in rows]
