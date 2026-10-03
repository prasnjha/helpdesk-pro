"""Internal note rows. Append-only: insert and read only, never shown to customers
(agent-workbench_spec.md AC-07).
"""

from __future__ import annotations

from sqlalchemy import Connection, Engine, text

from src.types.models import TicketNoteRecord


def insert(conn: Connection, *, ticket_id: str, author_id: str, body: str, created_at: str) -> int:
    result = conn.execute(
        text(
            "INSERT INTO ticket_notes (ticket_id, author_id, body, created_at) "
            "VALUES (:ticket_id, :author_id, :body, :created_at)"
        ),
        {"ticket_id": ticket_id, "author_id": author_id, "body": body, "created_at": created_at},
    )
    return int(result.lastrowid)


def list_for_ticket(engine: Engine, ticket_id: str) -> list[TicketNoteRecord]:
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT id, ticket_id, author_id, body, created_at "
                    "FROM ticket_notes WHERE ticket_id = :id ORDER BY id"
                ),
                {"id": ticket_id},
            )
            .mappings()
            .all()
        )
        return [TicketNoteRecord(**row) for row in rows]
