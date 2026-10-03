"""POST /api/tickets — customer intake with routing (AC-01, AC-02, E2-S3)."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import Engine

from src.api.deps import get_clock, get_engine, require_role
from src.service.ticket_service import create_ticket as create_ticket_service
from src.service.ticket_service import list_my_tickets
from src.types.clock import Clock
from src.types.models import UserRecord

router = APIRouter(prefix="/api/tickets")


class Attachment(BaseModel):
    file_name: str
    size_bytes: int


class CreateTicketRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    category: Literal["Billing", "Technical", "Account"]
    priority: Literal["Critical", "High", "Medium", "Low"]
    attachments: list[Attachment] | None = None


class QueueOut(BaseModel):
    slug: str
    name: str


class CreateTicketResponse(BaseModel):
    id: str
    status: str
    category: str
    priority: str
    queue: QueueOut
    customer_id: str
    created_at: str


class TicketSummaryOut(BaseModel):
    id: str
    title: str
    status: str
    priority: str
    category: str
    updated_at: str


@router.get("", response_model=list[TicketSummaryOut])
def list_tickets(
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(require_role("customer")),
) -> list[TicketSummaryOut]:
    rows = list_my_tickets(engine, user.id)
    return [TicketSummaryOut(**vars(row)) for row in rows]


@router.post("", response_model=CreateTicketResponse, status_code=201)
def create_ticket(
    payload: CreateTicketRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("customer")),
) -> CreateTicketResponse:
    ticket = create_ticket_service(
        engine,
        clock,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        customer_id=user.id,
    )
    return CreateTicketResponse(
        id=ticket.id,
        status=ticket.status,
        category=ticket.category,
        priority=ticket.priority,
        queue=QueueOut(slug=ticket.queue.slug, name=ticket.queue.name),
        customer_id=ticket.customer_id,
        created_at=ticket.created_at,
    )
