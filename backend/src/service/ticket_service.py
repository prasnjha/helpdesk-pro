"""Ticket orchestration: intake (ticket-intake_spec.md, routing_spec.md), claim,
reassign, status, notes and replies (agent-workbench_spec.md, ticket-lifecycle_spec.md).
"""

from __future__ import annotations

from sqlalchemy import Engine

from src.repository import ticket_repository, user_repository
from src.types.clock import Clock
from src.types.errors import NotFoundError, ValidationError
from src.types.models import TicketRecord, TicketReplyRecord, TicketSummary


def list_my_tickets(engine: Engine, customer_id: str) -> list[TicketSummary]:
    return ticket_repository.list_for_customer(engine, customer_id)


def create_ticket(
    engine: Engine,
    clock: Clock,
    *,
    title: str,
    description: str,
    category: str,
    priority: str,
    customer_id: str,
) -> TicketRecord:
    return ticket_repository.create_ticket(
        engine,
        title=title,
        description=description,
        category=category,
        priority=priority,
        customer_id=customer_id,
        now=clock.now(),
    )


def get_ticket_for_customer(engine: Engine, ticket_id: str, customer_id: str) -> TicketRecord:
    """Return the ticket if `customer_id` owns it, else 404 (never 403)."""
    ticket = ticket_repository.get_by_id(engine, ticket_id)
    if ticket is None or ticket.customer_id != customer_id:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    return ticket


def get_ticket_for_agent(engine: Engine, ticket_id: str) -> TicketRecord:
    ticket = ticket_repository.get_by_id(engine, ticket_id)
    if ticket is None:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    return ticket


def claim_ticket(
    engine: Engine, clock: Clock, *, ticket_id: str, actor_id: str, version: int
) -> TicketRecord:
    return ticket_repository.claim(
        engine, ticket_id=ticket_id, actor_id=actor_id, version=version, now=clock.now()
    )


def reassign_ticket(
    engine: Engine,
    clock: Clock,
    *,
    ticket_id: str,
    actor_id: str,
    assignee_id: str,
    version: int,
) -> TicketRecord:
    target = user_repository.get_by_id_via_engine(engine, assignee_id)
    if target is None or target.role != "agent" or not target.active:
        raise ValidationError("assignee_id", f"'{assignee_id}' is not an active agent")
    return ticket_repository.reassign(
        engine,
        ticket_id=ticket_id,
        actor_id=actor_id,
        assignee_id=assignee_id,
        version=version,
        now=clock.now(),
    )


def change_ticket_status(
    engine: Engine,
    clock: Clock,
    *,
    ticket_id: str,
    actor_id: str,
    to_status: str,
    version: int,
    correlation_id: str | None = None,
) -> TicketRecord:
    return ticket_repository.change_status(
        engine,
        ticket_id=ticket_id,
        actor_id=actor_id,
        to_status=to_status,
        version=version,
        now=clock.now(),
        correlation_id=correlation_id,
    )


def add_note(
    engine: Engine, clock: Clock, *, ticket_id: str, author_id: str, body: str
) -> tuple[int, str]:
    return ticket_repository.add_note(
        engine, ticket_id=ticket_id, author_id=author_id, body=body, now=clock.now()
    )


def add_reply(
    engine: Engine,
    clock: Clock,
    *,
    ticket_id: str,
    author_id: str,
    author_role: str,
    body: str,
) -> tuple[TicketReplyRecord, TicketRecord]:
    return ticket_repository.add_reply(
        engine,
        ticket_id=ticket_id,
        author_id=author_id,
        author_role=author_role,
        body=body,
        now=clock.now(),
    )
