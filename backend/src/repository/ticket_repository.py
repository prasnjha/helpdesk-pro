"""Ticket writes. Routing and the ticket insert share one transaction (ASM-S7).

Ticket history is append-only: insert and read only, no update or delete.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Connection, Engine, text

from src.domain.routing import resolve_queue_id
from src.domain.ticket_lifecycle import resolve_customer_reply_status, validate_transition
from src.repository import (
    assignment_repository,
    note_repository,
    reply_repository,
    routing_repository,
    sla_policy_repository,
    team_repository,
)
from src.types.errors import (
    NotFoundError,
    RoutingRuleMissingError,
    TicketClosedImmutableError,
    VersionConflictError,
)
from src.types.models import (
    TicketHistoryRecord,
    TicketRecord,
    TicketReplyRecord,
    TicketSummary,
)


def create_ticket(
    engine: Engine,
    *,
    title: str,
    description: str,
    category: str,
    priority: str,
    customer_id: str,
    now: datetime,
) -> TicketRecord:
    """Route and insert a ticket in one transaction. No partial row on failure."""
    with engine.begin() as conn:
        rules = routing_repository.get_all_rules(conn)
        try:
            queue_id = resolve_queue_id(category, rules)
        except RoutingRuleMissingError:
            # Raising here aborts the `with` block, rolling back; nothing is
            # written when there is no rule for the category.
            raise

        policy_version_id = sla_policy_repository.get_active_version_id(conn, priority)
        if policy_version_id is None:
            raise RoutingRuleMissingError(f"No SLA policy for priority '{priority}'")

        created_at = now.isoformat()
        result = conn.execute(
            text(
                "INSERT INTO tickets "
                "(id, title, description, category, priority, status, queue_id, "
                " customer_id, assignee_id, escalated, sla_policy_version_id, "
                " version, created_at, updated_at) "
                "VALUES (NULL, :title, :description, :category, :priority, 'OPEN', "
                " :queue_id, :customer_id, NULL, 0, :policy_version_id, 1, "
                " :created_at, :created_at)"
            ),
            {
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "queue_id": queue_id,
                "customer_id": customer_id,
                "policy_version_id": policy_version_id,
                "created_at": created_at,
            },
        )
        seq = result.lastrowid
        ticket_id = f"HD-{seq:06d}"
        conn.execute(
            text("UPDATE tickets SET id = :id WHERE seq = :seq"),
            {"id": ticket_id, "seq": seq},
        )
        conn.execute(
            text(
                "INSERT INTO ticket_history "
                "(ticket_id, event, from_state, to_state, actor_id, correlation_id, created_at) "
                "VALUES (:ticket_id, 'ROUTED', NULL, 'OPEN', 'system', NULL, :created_at)"
            ),
            {"ticket_id": ticket_id, "created_at": created_at},
        )
        queue = team_repository.get_by_id(conn, queue_id)
        assert queue is not None

    return TicketRecord(
        id=ticket_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status="OPEN",
        queue=queue,
        customer_id=customer_id,
        assignee_id=None,
        escalated=False,
        sla_policy_version_id=policy_version_id,
        version=1,
        created_at=created_at,
        updated_at=created_at,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )


def list_for_customer(engine: Engine, customer_id: str) -> list[TicketSummary]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT id, title, status, priority, category, updated_at "
                "FROM tickets WHERE customer_id = :customer_id ORDER BY seq"
            ),
            {"customer_id": customer_id},
        ).mappings().all()
        return [TicketSummary(**row) for row in rows]


def list_for_queue(
    engine: Engine,
    *,
    queue_id: int,
    priority: str | None = None,
    status: str | None = None,
    escalated: bool | None = None,
) -> list[TicketRecord]:
    clauses = ["queue_id = :queue_id"]
    params: dict[str, object] = {"queue_id": queue_id}
    if priority is not None:
        clauses.append("priority = :priority")
        params["priority"] = priority
    if status is not None:
        clauses.append("status = :status")
        params["status"] = status
    if escalated is not None:
        clauses.append("escalated = :escalated")
        params["escalated"] = 1 if escalated else 0
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT * FROM tickets WHERE " + " AND ".join(clauses) + " ORDER BY seq"
                ),
                params,
            )
            .mappings()
            .all()
        )
        queue = team_repository.get_by_id(conn, queue_id)
        assert queue is not None
        return [
            TicketRecord(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                category=row["category"],
                priority=row["priority"],
                status=row["status"],
                queue=queue,
                customer_id=row["customer_id"],
                assignee_id=row["assignee_id"],
                escalated=bool(row["escalated"]),
                sla_policy_version_id=row["sla_policy_version_id"],
                version=row["version"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                response_stopped_at=row["response_stopped_at"],
                resolution_stopped_at=row["resolution_stopped_at"],
            )
            for row in rows
        ]


def count_tickets(engine: Engine) -> int:
    with engine.connect() as conn:
        return int(conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one())


def history_events_for(engine: Engine, ticket_id: str) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT event FROM ticket_history WHERE ticket_id = :id"),
            {"id": ticket_id},
        ).all()
        return [row[0] for row in rows]


def list_history_for(engine: Engine, ticket_id: str) -> list[TicketHistoryRecord]:
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT id, ticket_id, event, from_state, to_state, actor_id, "
                    "correlation_id, created_at FROM ticket_history "
                    "WHERE ticket_id = :id ORDER BY id"
                ),
                {"id": ticket_id},
            )
            .mappings()
            .all()
        )
        return [TicketHistoryRecord(**row) for row in rows]


def _get_by_id(conn: Connection, ticket_id: str) -> TicketRecord | None:
    row = (
        conn.execute(text("SELECT * FROM tickets WHERE id = :id"), {"id": ticket_id})
        .mappings()
        .first()
    )
    if row is None:
        return None
    queue = team_repository.get_by_id(conn, row["queue_id"])
    assert queue is not None
    return TicketRecord(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        category=row["category"],
        priority=row["priority"],
        status=row["status"],
        queue=queue,
        customer_id=row["customer_id"],
        assignee_id=row["assignee_id"],
        escalated=bool(row["escalated"]),
        sla_policy_version_id=row["sla_policy_version_id"],
        version=row["version"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        response_stopped_at=row["response_stopped_at"],
        resolution_stopped_at=row["resolution_stopped_at"],
    )


def get_by_id(engine: Engine, ticket_id: str) -> TicketRecord | None:
    with engine.connect() as conn:
        return _get_by_id(conn, ticket_id)


def get_by_id_in_conn(conn: Connection, ticket_id: str) -> TicketRecord | None:
    """Same read as `get_by_id`, for callers already inside a transaction."""
    return _get_by_id(conn, ticket_id)


def escalate(
    conn: Connection, *, ticket_id: str, to_queue_id: int, now: datetime
) -> TicketRecord:
    """Move `ticket_id` to `to_queue_id` and set `escalated` (escalation_spec.md).
    The status is never changed: ESCALATED is a flag, not a status (A-05).
    Writes one TicketHistory row with event ESCALATED, actor `system`. Callers
    own the transaction (`conn`) so this shares it with the breach SlaEvent
    write it always accompanies.
    """
    created_at = now.isoformat()
    conn.execute(
        text(
            "UPDATE tickets SET escalated = 1, queue_id = :to_queue_id, "
            "version = version + 1, updated_at = :now WHERE id = :id"
        ),
        {"to_queue_id": to_queue_id, "now": created_at, "id": ticket_id},
    )
    conn.execute(
        text(
            "INSERT INTO ticket_history "
            "(ticket_id, event, from_state, to_state, actor_id, correlation_id, created_at) "
            "VALUES (:ticket_id, 'ESCALATED', NULL, NULL, 'system', NULL, :created_at)"
        ),
        {"ticket_id": ticket_id, "created_at": created_at},
    )
    updated = _get_by_id(conn, ticket_id)
    assert updated is not None
    return updated


def _require_ticket(conn: Connection, ticket_id: str) -> TicketRecord:
    ticket = _get_by_id(conn, ticket_id)
    if ticket is None:
        raise NotFoundError(f"Ticket '{ticket_id}' not found")
    return ticket


def _require_version(ticket: TicketRecord, version: int) -> None:
    if ticket.version != version:
        raise VersionConflictError(f"Ticket '{ticket.id}' was updated by someone else")


def claim(
    engine: Engine, *, ticket_id: str, actor_id: str, version: int, now: datetime
) -> TicketRecord:
    """Set the assignee to `actor_id`; an `OPEN` ticket also moves to `IN_PROGRESS`
    (ASM-S1). The assignment insert and the ticket update share one transaction.
    """
    created_at = now.isoformat()
    with engine.begin() as conn:
        ticket = _require_ticket(conn, ticket_id)
        _require_version(ticket, version)
        if ticket.status == "CLOSED":
            raise TicketClosedImmutableError("CLOSED tickets accept no further writes")
        new_status = "IN_PROGRESS" if ticket.status == "OPEN" else ticket.status
        result = conn.execute(
            text(
                "UPDATE tickets SET assignee_id = :to_user_id, status = :status, "
                "version = version + 1, updated_at = :now WHERE id = :id AND version = :version"
            ),
            {
                "to_user_id": actor_id,
                "status": new_status,
                "now": created_at,
                "id": ticket_id,
                "version": version,
            },
        )
        if result.rowcount == 0:
            raise VersionConflictError(f"Ticket '{ticket_id}' was updated by someone else")
        assignment_repository.insert(
            conn,
            ticket_id=ticket_id,
            from_user_id=ticket.assignee_id,
            to_user_id=actor_id,
            actor_id=actor_id,
            created_at=created_at,
        )
        if new_status != ticket.status:
            conn.execute(
                text(
                    "INSERT INTO ticket_history "
                    "(ticket_id, event, from_state, to_state, actor_id, "
                    "correlation_id, created_at) "
                    "VALUES (:ticket_id, 'STATUS_CHANGED', :from_state, :to_state, "
                    ":actor_id, NULL, :created_at)"
                ),
                {
                    "ticket_id": ticket_id,
                    "from_state": ticket.status,
                    "to_state": new_status,
                    "actor_id": actor_id,
                    "created_at": created_at,
                },
            )
        updated = _get_by_id(conn, ticket_id)
        assert updated is not None
        return updated


def reassign(
    engine: Engine,
    *,
    ticket_id: str,
    actor_id: str,
    assignee_id: str,
    version: int,
    now: datetime,
) -> TicketRecord:
    """Change the assignee. The status does not change (ASM-S1)."""
    created_at = now.isoformat()
    with engine.begin() as conn:
        ticket = _require_ticket(conn, ticket_id)
        _require_version(ticket, version)
        if ticket.status == "CLOSED":
            raise TicketClosedImmutableError("CLOSED tickets accept no further writes")
        result = conn.execute(
            text(
                "UPDATE tickets SET assignee_id = :to_user_id, version = version + 1, "
                "updated_at = :now WHERE id = :id AND version = :version"
            ),
            {"to_user_id": assignee_id, "now": created_at, "id": ticket_id, "version": version},
        )
        if result.rowcount == 0:
            raise VersionConflictError(f"Ticket '{ticket_id}' was updated by someone else")
        assignment_repository.insert(
            conn,
            ticket_id=ticket_id,
            from_user_id=ticket.assignee_id,
            to_user_id=assignee_id,
            actor_id=actor_id,
            created_at=created_at,
        )
        updated = _get_by_id(conn, ticket_id)
        assert updated is not None
        return updated


def change_status(
    engine: Engine,
    *,
    ticket_id: str,
    actor_id: str,
    to_status: str,
    version: int,
    now: datetime,
    correlation_id: str | None = None,
) -> TicketRecord:
    """Apply one of the six valid status edges and write one TicketHistory row.

    Reaching `RESOLVED` stops the resolution timer, and the response timer too
    if it is still running (sla-policy-evaluator skill).
    """
    created_at = now.isoformat()
    with engine.begin() as conn:
        ticket = _require_ticket(conn, ticket_id)
        _require_version(ticket, version)
        validate_transition(ticket.status, to_status)
        response_stopped_at = ticket.response_stopped_at
        resolution_stopped_at = ticket.resolution_stopped_at
        if to_status == "RESOLVED":
            resolution_stopped_at = created_at
            if response_stopped_at is None:
                response_stopped_at = created_at
        result = conn.execute(
            text(
                "UPDATE tickets SET status = :status, version = version + 1, "
                "updated_at = :now, response_stopped_at = :response_stopped_at, "
                "resolution_stopped_at = :resolution_stopped_at "
                "WHERE id = :id AND version = :version"
            ),
            {
                "status": to_status,
                "now": created_at,
                "response_stopped_at": response_stopped_at,
                "resolution_stopped_at": resolution_stopped_at,
                "id": ticket_id,
                "version": version,
            },
        )
        if result.rowcount == 0:
            raise VersionConflictError(f"Ticket '{ticket_id}' was updated by someone else")
        conn.execute(
            text(
                "INSERT INTO ticket_history "
                "(ticket_id, event, from_state, to_state, actor_id, correlation_id, created_at) "
                "VALUES (:ticket_id, 'STATUS_CHANGED', :from_state, :to_state, "
                ":actor_id, :correlation_id, :created_at)"
            ),
            {
                "ticket_id": ticket_id,
                "from_state": ticket.status,
                "to_state": to_status,
                "actor_id": actor_id,
                "correlation_id": correlation_id,
                "created_at": created_at,
            },
        )
        updated = _get_by_id(conn, ticket_id)
        assert updated is not None
        return updated


def add_note(
    engine: Engine, *, ticket_id: str, author_id: str, body: str, now: datetime
) -> tuple[int, str]:
    """Insert one internal note. Returns `(note_id, created_at)`."""
    created_at = now.isoformat()
    with engine.begin() as conn:
        ticket = _require_ticket(conn, ticket_id)
        if ticket.status == "CLOSED":
            raise TicketClosedImmutableError("CLOSED tickets accept no further writes")
        note_id = note_repository.insert(
            conn, ticket_id=ticket_id, author_id=author_id, body=body, created_at=created_at
        )
        return note_id, created_at


def add_reply(
    engine: Engine,
    *,
    ticket_id: str,
    author_id: str,
    author_role: str,
    body: str,
    now: datetime,
) -> tuple[TicketReplyRecord, TicketRecord]:
    """Insert a reply and apply the lifecycle-spec status move (if any), in one
    transaction (AC-08). A customer reply on someone else's ticket is reported as
    `NotFoundError`, never `ForbiddenError` (api-contracts.md).
    """
    created_at = now.isoformat()
    with engine.begin() as conn:
        ticket = _require_ticket(conn, ticket_id)
        if author_role == "customer":
            if ticket.customer_id != author_id:
                raise NotFoundError(f"Ticket '{ticket_id}' not found")
            new_status = resolve_customer_reply_status(ticket.status)
        else:
            if ticket.status == "CLOSED":
                raise TicketClosedImmutableError("CLOSED tickets accept no further writes")
            new_status = ticket.status

        reply_id = reply_repository.insert(
            conn,
            ticket_id=ticket_id,
            author_id=author_id,
            author_role=author_role,
            body=body,
            created_at=created_at,
        )

        # The response timer stops at the first PUBLIC agent reply only
        # (sla-policy-evaluator skill); internal notes and customer replies
        # never stop it, and a later agent reply never moves it again.
        if author_role == "agent" and ticket.response_stopped_at is None:
            conn.execute(
                text("UPDATE tickets SET response_stopped_at = :stopped_at WHERE id = :id"),
                {"stopped_at": created_at, "id": ticket_id},
            )

        if new_status != ticket.status:
            conn.execute(
                text(
                    "UPDATE tickets SET status = :status, version = version + 1, "
                    "updated_at = :now WHERE id = :id"
                ),
                {"status": new_status, "now": created_at, "id": ticket_id},
            )
            conn.execute(
                text(
                    "INSERT INTO ticket_history "
                    "(ticket_id, event, from_state, to_state, actor_id, "
                    "correlation_id, created_at) "
                    "VALUES (:ticket_id, 'STATUS_CHANGED', :from_state, :to_state, "
                    ":actor_id, NULL, :created_at)"
                ),
                {
                    "ticket_id": ticket_id,
                    "from_state": ticket.status,
                    "to_state": new_status,
                    "actor_id": author_id,
                    "created_at": created_at,
                },
            )

        updated = _get_by_id(conn, ticket_id)
        assert updated is not None

    reply = TicketReplyRecord(
        id=reply_id,
        ticket_id=ticket_id,
        author_id=author_id,
        author_role=author_role,
        body=body,
        created_at=created_at,
    )
    return reply, updated
