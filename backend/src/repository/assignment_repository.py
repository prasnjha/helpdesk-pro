"""Assignment (claim/reassign) rows. Append-only: insert and read only, no update
or delete method exists on this module (agent-workbench_spec.md AC-03; checked by
tests/architecture/test_assignment_repository_append_only.py).
"""

from __future__ import annotations

from sqlalchemy import Connection, Engine, text

from src.types.models import AssignmentRecord


def insert(
    conn: Connection,
    *,
    ticket_id: str,
    from_user_id: str | None,
    to_user_id: str,
    actor_id: str,
    created_at: str,
) -> int:
    result = conn.execute(
        text(
            "INSERT INTO assignments (ticket_id, from_user_id, to_user_id, actor_id, created_at) "
            "VALUES (:ticket_id, :from_user_id, :to_user_id, :actor_id, :created_at)"
        ),
        {
            "ticket_id": ticket_id,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "actor_id": actor_id,
            "created_at": created_at,
        },
    )
    return int(result.lastrowid)


def list_for_ticket(engine: Engine, ticket_id: str) -> list[AssignmentRecord]:
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT id, ticket_id, from_user_id, to_user_id, actor_id, created_at "
                    "FROM assignments WHERE ticket_id = :id ORDER BY id"
                ),
                {"id": ticket_id},
            )
            .mappings()
            .all()
        )
        return [AssignmentRecord(**row) for row in rows]
