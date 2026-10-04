"""GET /api/tickets/{id}/sla orchestration (AC-05). Customers may read only
their own ticket's timers; agents and admins may read any (api-contracts.md).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine

from src.domain.sla import SlaSnapshot, evaluate_sla
from src.repository import sla_policy_repository, ticket_repository
from src.types.clock import Clock
from src.types.errors import NotFoundError


def _parse(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)


def _snapshot(engine: Engine, clock: Clock, ticket_id: str) -> SlaSnapshot | None:
    ticket = ticket_repository.get_by_id(engine, ticket_id)
    if ticket is None:
        return None
    with engine.connect() as conn:
        response_target, resolution_target = sla_policy_repository.get_targets(
            conn, ticket.sla_policy_version_id
        )
    created_at = _parse(ticket.created_at)
    assert created_at is not None
    return evaluate_sla(
        created_at=created_at,
        now=clock.now(),
        response_target_minutes=response_target,
        resolution_target_minutes=resolution_target,
        response_stopped_at=_parse(ticket.response_stopped_at),
        resolution_stopped_at=_parse(ticket.resolution_stopped_at),
    )


def get_snapshot_for_customer(
    engine: Engine, clock: Clock, ticket_id: str, customer_id: str
) -> SlaSnapshot:
    ticket = ticket_repository.get_by_id(engine, ticket_id)
    if ticket is None or ticket.customer_id != customer_id:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    snapshot = _snapshot(engine, clock, ticket_id)
    assert snapshot is not None
    return snapshot


def get_snapshot_for_agent(engine: Engine, clock: Clock, ticket_id: str) -> SlaSnapshot:
    snapshot = _snapshot(engine, clock, ticket_id)
    if snapshot is None:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    return snapshot
