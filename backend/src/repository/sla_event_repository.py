"""SlaEvent reads and inserts (escalation_spec.md, E4-S3). Append-only:
insert and read only, no update or delete.
"""

from __future__ import annotations

from sqlalchemy import Connection, text

from src.types.models import SlaEventRecord


def insert(
    conn: Connection,
    *,
    ticket_id: str,
    event: str,
    timer: str | None,
    breached_at: str | None,
    created_at: str,
) -> int:
    result = conn.execute(
        text(
            "INSERT INTO sla_event (ticket_id, event, timer, breached_at, created_at) "
            "VALUES (:ticket_id, :event, :timer, :breached_at, :created_at)"
        ),
        {
            "ticket_id": ticket_id,
            "event": event,
            "timer": timer,
            "breached_at": breached_at,
            "created_at": created_at,
        },
    )
    new_id = result.lastrowid
    assert new_id is not None
    return int(new_id)


def list_for_ticket(conn: Connection, ticket_id: str) -> list[SlaEventRecord]:
    rows = (
        conn.execute(
            text(
                "SELECT id, ticket_id, event, timer, breached_at, created_at "
                "FROM sla_event WHERE ticket_id = :id ORDER BY id"
            ),
            {"id": ticket_id},
        )
        .mappings()
        .all()
    )
    return [SlaEventRecord(**row) for row in rows]


def has_breach(conn: Connection, ticket_id: str, timer: str) -> bool:
    event = "BREACHED_RESPONSE" if timer == "response" else "BREACHED_RESOLUTION"
    row = conn.execute(
        text(
            "SELECT 1 FROM sla_event WHERE ticket_id = :ticket_id AND event = :event LIMIT 1"
        ),
        {"ticket_id": ticket_id, "event": event},
    ).first()
    return row is not None


def has_escalation(conn: Connection, ticket_id: str) -> bool:
    row = conn.execute(
        text(
            "SELECT 1 FROM sla_event WHERE ticket_id = :ticket_id "
            "AND event = 'ESCALATED' LIMIT 1"
        ),
        {"ticket_id": ticket_id},
    ).first()
    return row is not None
