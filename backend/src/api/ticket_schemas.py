"""Pydantic request and response models for the ticket endpoints.

Moved out of routers/tickets.py to keep that file under the 300-line rule.
Shapes are unchanged; the router imports these names.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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


class TicketAssignmentOut(BaseModel):
    id: int
    ticket_id: str
    from_user_id: str | None
    to_user_id: str
    actor_id: str
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
    assignments: list[TicketAssignmentOut]


class SlaTimerOut(BaseModel):
    target_minutes: int
    elapsed_minutes: int
    state: str
    stopped_at: str | None


class SlaSnapshotOut(BaseModel):
    response: SlaTimerOut
    resolution: SlaTimerOut


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
