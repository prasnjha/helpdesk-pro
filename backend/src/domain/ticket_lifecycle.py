"""Ticket status state machine (ticket-lifecycle_spec.md).

No FastAPI or SQLAlchemy imports here (backend/src/domain/CLAUDE.md).
"""

from __future__ import annotations

from src.types.errors import InvalidTicketStateError

VALID_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
        ("OPEN", "IN_PROGRESS"),
        ("IN_PROGRESS", "PENDING_CUSTOMER"),
        ("PENDING_CUSTOMER", "RESOLVED"),
        ("RESOLVED", "CLOSED"),
        ("PENDING_CUSTOMER", "OPEN"),
        ("IN_PROGRESS", "RESOLVED"),
    }
)

_NO_REPLY_STATES = frozenset({"RESOLVED", "CLOSED"})


def validate_transition(current_status: str, to_status: str) -> None:
    """Raise `InvalidTicketStateError` unless `current_status` -> `to_status` is one
    of the six valid edges (Section 2, ticket-lifecycle_spec.md). A `CLOSED` ticket has
    no outgoing edge, so every move from it lands here too.
    """
    if (current_status, to_status) not in VALID_EDGES:
        raise InvalidTicketStateError(
            f"Cannot transition from '{current_status}' to '{to_status}'"
        )


def resolve_customer_reply_status(current_status: str) -> str:
    """Return the ticket status after a customer reply, or raise when replies are
    refused outright. `PENDING_CUSTOMER` moves to `OPEN`; `OPEN` and `IN_PROGRESS`
    are unchanged (A-18); `RESOLVED` and `CLOSED` refuse the reply (A-17).
    """
    if current_status in _NO_REPLY_STATES:
        raise InvalidTicketStateError(f"Cannot reply to a ticket in '{current_status}'")
    if current_status == "PENDING_CUSTOMER":
        return "OPEN"
    return current_status
