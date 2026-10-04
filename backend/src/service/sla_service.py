"""GET /api/tickets/{id}/sla orchestration (AC-05). Customers may read only
their own ticket's timers; agents and admins may read any (api-contracts.md).
"""

from __future__ import annotations

from sqlalchemy import Engine

from src.domain.sla import SlaSnapshot
from src.repository import sla_repository, ticket_repository
from src.types.clock import Clock
from src.types.errors import NotFoundError


def get_snapshot_for_customer(
    engine: Engine, clock: Clock, ticket_id: str, customer_id: str
) -> SlaSnapshot:
    ticket = ticket_repository.get_by_id(engine, ticket_id)
    if ticket is None or ticket.customer_id != customer_id:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    snapshot = sla_repository.evaluate_and_escalate(engine, ticket_id=ticket_id, now=clock.now())
    assert snapshot is not None
    return snapshot


def get_snapshot_for_agent(engine: Engine, clock: Clock, ticket_id: str) -> SlaSnapshot:
    snapshot = sla_repository.evaluate_and_escalate(engine, ticket_id=ticket_id, now=clock.now())
    if snapshot is None:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    return snapshot
