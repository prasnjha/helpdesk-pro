"""Ticket endpoints: customer intake (AC-01, AC-02, E2-S3), detail, claim and
reassign (AC-03, E3-S2), status transitions (AC-04, E3-S1), notes and replies
(AC-07, AC-08, E3-S3, E3-S4).
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import Engine

from src.api.deps import get_clock, get_current_user, get_engine, require_role
from src.domain.sla import SlaSnapshot
from src.repository import note_repository, reply_repository, ticket_repository
from src.service.sla_service import get_snapshot_for_agent, get_snapshot_for_customer
from src.service.ticket_service import add_note as add_note_service
from src.service.ticket_service import add_reply as add_reply_service
from src.service.ticket_service import change_ticket_status as change_ticket_status_service
from src.service.ticket_service import claim_ticket as claim_ticket_service
from src.service.ticket_service import create_ticket as create_ticket_service
from src.service.ticket_service import (
    get_ticket_for_agent,
    get_ticket_for_customer,
    list_my_tickets,
)
from src.service.ticket_service import reassign_ticket as reassign_ticket_service
from src.types.clock import Clock
from src.types.errors import MethodNotAllowedError
from src.types.models import TicketRecord, UserRecord

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


class TicketReplyOut(BaseModel):
    id: int
    ticket_id: str
    author_id: str
    author_role: str
    body: str
    created_at: str


class TicketNoteOut(BaseModel):
    id: int
    ticket_id: str
    author_id: str
    body: str
    created_at: str


class TicketHistoryOut(BaseModel):
    id: int
    ticket_id: str
    event: str
    from_state: str | None
    to_state: str | None
    actor_id: str
    correlation_id: str | None
    created_at: str


class TicketDetailOut(BaseModel):
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    queue: QueueOut
    customer_id: str
    assignee_id: str | None
    escalated: bool
    version: int
    sla_policy_version_id: int
    created_at: str
    updated_at: str
    replies: list[TicketReplyOut]
    notes: list[TicketNoteOut]
    history: list[TicketHistoryOut]


class SlaTimerOut(BaseModel):
    target_minutes: int
    elapsed_minutes: int
    state: str
    stopped_at: str | None


class SlaSnapshotOut(BaseModel):
    response: SlaTimerOut
    resolution: SlaTimerOut


def _sla_snapshot_out(snapshot: SlaSnapshot) -> SlaSnapshotOut:
    return SlaSnapshotOut(
        response=SlaTimerOut(
            target_minutes=snapshot.response.target_minutes,
            elapsed_minutes=snapshot.response.elapsed_minutes,
            state=snapshot.response.state,
            stopped_at=snapshot.response.stopped_at.isoformat()
            if snapshot.response.stopped_at
            else None,
        ),
        resolution=SlaTimerOut(
            target_minutes=snapshot.resolution.target_minutes,
            elapsed_minutes=snapshot.resolution.elapsed_minutes,
            state=snapshot.resolution.state,
            stopped_at=snapshot.resolution.stopped_at.isoformat()
            if snapshot.resolution.stopped_at
            else None,
        ),
    )


class ClaimRequest(BaseModel):
    version: int


class ReassignRequest(BaseModel):
    assignee_id: str
    version: int


class AssignmentResponse(BaseModel):
    id: str
    status: str
    assignee_id: str | None


class StatusRequest(BaseModel):
    to_status: Literal["OPEN", "IN_PROGRESS", "PENDING_CUSTOMER", "RESOLVED", "CLOSED"]
    version: int


class StatusResponse(BaseModel):
    id: str
    status: str


class NoteRequest(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class NoteResponse(BaseModel):
    id: int
    ticket_id: str
    author_id: str
    body: str
    created_at: str


class ReplyRequest(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class ReplyResponse(BaseModel):
    id: int
    ticket_id: str
    author_role: str
    body: str
    created_at: str
    status: str


def _queue_out(ticket: TicketRecord) -> QueueOut:
    return QueueOut(slug=ticket.queue.slug, name=ticket.queue.name)


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


@router.get("/{ticket_id}", response_model=TicketDetailOut)
def get_ticket_detail(
    ticket_id: str,
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(get_current_user),
) -> TicketDetailOut:
    if user.role == "customer":
        ticket = get_ticket_for_customer(engine, ticket_id, user.id)
        notes: list[TicketNoteOut] = []
        history: list[TicketHistoryOut] = []
    else:
        ticket = get_ticket_for_agent(engine, ticket_id)
        note_rows = note_repository.list_for_ticket(engine, ticket_id)
        notes = [TicketNoteOut(**vars(n)) for n in note_rows]
        history_rows = ticket_repository.list_history_for(engine, ticket_id)
        history = [TicketHistoryOut(**vars(h)) for h in history_rows]
    reply_rows = reply_repository.list_for_ticket(engine, ticket_id)
    replies = [TicketReplyOut(**vars(r)) for r in reply_rows]
    return TicketDetailOut(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        queue=_queue_out(ticket),
        customer_id=ticket.customer_id,
        assignee_id=ticket.assignee_id,
        escalated=ticket.escalated,
        version=ticket.version,
        sla_policy_version_id=ticket.sla_policy_version_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        replies=replies,
        notes=notes,
        history=history,
    )


@router.get("/{ticket_id}/sla", response_model=SlaSnapshotOut)
def get_ticket_sla(
    ticket_id: str,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(get_current_user),
) -> SlaSnapshotOut:
    if user.role == "customer":
        snapshot = get_snapshot_for_customer(engine, clock, ticket_id, user.id)
    else:
        snapshot = get_snapshot_for_agent(engine, clock, ticket_id)
    return _sla_snapshot_out(snapshot)


@router.post("/{ticket_id}/claim", response_model=AssignmentResponse)
def claim_ticket(
    ticket_id: str,
    payload: ClaimRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> AssignmentResponse:
    ticket = claim_ticket_service(
        engine, clock, ticket_id=ticket_id, actor_id=user.id, version=payload.version
    )
    return AssignmentResponse(id=ticket.id, status=ticket.status, assignee_id=ticket.assignee_id)


@router.post("/{ticket_id}/reassign", response_model=AssignmentResponse)
def reassign_ticket(
    ticket_id: str,
    payload: ReassignRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> AssignmentResponse:
    ticket = reassign_ticket_service(
        engine,
        clock,
        ticket_id=ticket_id,
        actor_id=user.id,
        assignee_id=payload.assignee_id,
        version=payload.version,
    )
    return AssignmentResponse(id=ticket.id, status=ticket.status, assignee_id=ticket.assignee_id)


@router.post("/{ticket_id}/status", response_model=StatusResponse)
def set_ticket_status(
    ticket_id: str,
    payload: StatusRequest,
    request: Request,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> StatusResponse:
    correlation_id = request.headers.get("X-Correlation-Id")
    ticket = change_ticket_status_service(
        engine,
        clock,
        ticket_id=ticket_id,
        actor_id=user.id,
        to_status=payload.to_status,
        version=payload.version,
        correlation_id=correlation_id,
    )
    return StatusResponse(id=ticket.id, status=ticket.status)


@router.post("/{ticket_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    ticket_id: str,
    payload: NoteRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("agent", "admin")),
) -> NoteResponse:
    note_id, created_at = add_note_service(
        engine, clock, ticket_id=ticket_id, author_id=user.id, body=payload.body
    )
    return NoteResponse(
        id=note_id, ticket_id=ticket_id, author_id=user.id, body=payload.body, created_at=created_at
    )


@router.post("/{ticket_id}/replies", response_model=ReplyResponse, status_code=201)
def create_reply(
    ticket_id: str,
    payload: ReplyRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(get_current_user),
) -> ReplyResponse:
    author_role = "customer" if user.role == "customer" else "agent"
    reply, ticket = add_reply_service(
        engine,
        clock,
        ticket_id=ticket_id,
        author_id=user.id,
        author_role=author_role,
        body=payload.body,
    )
    return ReplyResponse(
        id=reply.id,
        ticket_id=reply.ticket_id,
        author_role=reply.author_role,
        body=reply.body,
        created_at=reply.created_at,
        status=ticket.status,
    )


@router.put("/{ticket_id}/notes/{note_id}")
@router.patch("/{ticket_id}/notes/{note_id}")
@router.delete("/{ticket_id}/notes/{note_id}")
def notes_are_immutable(
    ticket_id: str, note_id: int, user: UserRecord = Depends(get_current_user)
) -> None:
    raise MethodNotAllowedError("Notes are append-only; no update or delete method exists")


@router.put("/{ticket_id}/replies/{reply_id}")
@router.patch("/{ticket_id}/replies/{reply_id}")
@router.delete("/{ticket_id}/replies/{reply_id}")
def replies_are_immutable(
    ticket_id: str, reply_id: int, user: UserRecord = Depends(get_current_user)
) -> None:
    raise MethodNotAllowedError("Replies are append-only; no update or delete method exists")
