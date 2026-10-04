"""Agent workbench queue endpoint (api-contracts.md, "Agent queues")."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import Engine

from src.api.deps import get_clock, get_engine, require_role
from src.service.agent_queue_service import list_queue_tickets
from src.types.clock import Clock
from src.types.models import UserRecord

router = APIRouter(prefix="/api/agent/queues")


class QueueOut(BaseModel):
    slug: str
    name: str


class QueueTicketOut(BaseModel):
    id: str
    title: str
    priority: str
    status: str
    queue: QueueOut
    assignee_id: str | None
    escalated: bool
    response_state: str
    resolution_state: str


@router.get("/{queue}/tickets", response_model=list[QueueTicketOut])
def list_tickets_for_queue(
    queue: str,
    priority: Literal["Critical", "High", "Medium", "Low"] | None = None,
    status: Literal["OPEN", "IN_PROGRESS", "PENDING_CUSTOMER", "RESOLVED", "CLOSED"]
    | None = None,
    escalated: bool | None = None,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> list[QueueTicketOut]:
    rows = list_queue_tickets(
        engine,
        clock,
        queue_slug=queue,
        priority=priority,
        status=status,
        escalated=escalated,
    )
    return [
        QueueTicketOut(
            id=row.ticket.id,
            title=row.ticket.title,
            priority=row.ticket.priority,
            status=row.ticket.status,
            queue=QueueOut(slug=row.ticket.queue.slug, name=row.ticket.queue.name),
            assignee_id=row.ticket.assignee_id,
            escalated=row.ticket.escalated,
            response_state=row.response_state,
            resolution_state=row.resolution_state,
        )
        for row in rows
    ]
