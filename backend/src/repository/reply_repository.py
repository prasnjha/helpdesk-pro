"""Public reply rows. Append-only: insert and read only (ticket-lifecycle_spec.md,
agent-workbench_spec.md AC-07, AC-08).
"""

from __future__ import annotations

from sqlalchemy import Connection, Engine, text

from src.types.models import TicketReplyRecord


def insert(
    conn: Connection,
    *,
    ticket_id: str,
    author_id: str,
    author_role: str,
    body: str,
    created_at: str,
) -> int:
    result = conn.execute(
        text(
            "INSERT INTO ticket_replies (ticket_id, author_id, author_role, body, created_at) "
            "VALUES (:ticket_id, :author_id, :author_role, :body, :created_at)"
        ),
        {
            "ticket_id": ticket_id,
            "author_id": author_id,
            "author_role": author_role,
            "body": body,
            "created_at": created_at,
        },
    )
    return int(result.lastrowid)


def list_for_ticket(engine: Engine, ticket_id: str) -> list[TicketReplyRecord]:
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT id, ticket_id, author_id, author_role, body, created_at "
                    "FROM ticket_replies WHERE ticket_id = :id ORDER BY id"
                ),
                {"id": ticket_id},
            )
            .mappings()
            .all()
        )
        return [TicketReplyRecord(**row) for row in rows]
