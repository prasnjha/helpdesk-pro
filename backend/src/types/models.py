"""Plain data shapes shared across layers. No framework imports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserRecord:
    id: str
    username: str
    password_hash: str
    role: str
    team_id: int | None
    active: bool


@dataclass(frozen=True)
class QueueRef:
    slug: str
    name: str


@dataclass(frozen=True)
class TicketSummary:
    id: str
    title: str
    status: str
    priority: str
    category: str
    updated_at: str


@dataclass(frozen=True)
class TicketRecord:
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    queue: QueueRef
    customer_id: str
    assignee_id: str | None
    escalated: bool
    sla_policy_version_id: int
    version: int
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class AssignmentRecord:
    id: int
    ticket_id: str
    from_user_id: str | None
    to_user_id: str
    actor_id: str
    created_at: str


@dataclass(frozen=True)
class TicketNoteRecord:
    id: int
    ticket_id: str
    author_id: str
    body: str
    created_at: str


@dataclass(frozen=True)
class TicketReplyRecord:
    id: int
    ticket_id: str
    author_id: str
    author_role: str
    body: str
    created_at: str


@dataclass(frozen=True)
class SlaPolicyRecord:
    id: int
    priority: str
    version: int
    response_minutes: int
    resolution_minutes: int
    created_by: str
    published_at: str


@dataclass(frozen=True)
class TicketHistoryRecord:
    id: int
    ticket_id: str
    event: str
    from_state: str | None
    to_state: str | None
    actor_id: str
    correlation_id: str | None
    created_at: str
