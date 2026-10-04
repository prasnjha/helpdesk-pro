"""GET /api/agent/queues/{queue}/tickets orchestration (api-contracts.md).

Each ticket's SLA state is evaluated the same way as a ticket detail read:
every read evaluates the timers and escalates on breach (escalation_spec.md,
"no scheduler").
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from src.repository import sla_repository, team_repository, ticket_repository
from src.types.clock import Clock
from src.types.errors import NotFoundError
from src.types.models import TicketRecord


@dataclass(frozen=True)
class QueueTicketRow:
    ticket: TicketRecord
    response_state: str
    resolution_state: str


def list_queue_tickets(
    engine: Engine,
    clock: Clock,
    *,
    queue_slug: str,
    priority: str | None,
    status: str | None,
    escalated: bool | None,
) -> list[QueueTicketRow]:
    with engine.connect() as conn:
        queue_id = team_repository.get_id_by_slug(conn, queue_slug)
    if queue_id is None:
        raise NotFoundError(f"Queue '{queue_slug}' not found")

    tickets = ticket_repository.list_for_queue(
        engine, queue_id=queue_id, priority=priority, status=status, escalated=escalated
    )
    rows = []
    for ticket in tickets:
        snapshot = sla_repository.evaluate_and_escalate(
            engine, ticket_id=ticket.id, now=clock.now()
        )
        assert snapshot is not None
        rows.append(
            QueueTicketRow(
                ticket=ticket,
                response_state=snapshot.response.state,
                resolution_state=snapshot.resolution.state,
            )
        )
    return rows
