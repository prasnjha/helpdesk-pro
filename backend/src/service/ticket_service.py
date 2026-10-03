"""Ticket creation orchestration (ticket-intake_spec.md, routing_spec.md)."""

from __future__ import annotations

from sqlalchemy import Engine

from src.repository import ticket_repository
from src.types.clock import Clock
from src.types.models import TicketRecord, TicketSummary


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
