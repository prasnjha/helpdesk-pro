from __future__ import annotations

from src.repository.db import applied_migration_count
from src.repository.ticket_repository import create_ticket, history_events_for
from src.types.clock import TestClock
from src.types.errors import ValidationError


def test_E1S4_applied_migration_count_matches_migration_files(engine) -> None:
    assert applied_migration_count(engine) == 5


def test_E1S1_validation_error_carries_field_and_message() -> None:
    err = ValidationError("category", "Field 'category' is invalid")
    assert err.field == "category"
    assert err.to_envelope() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Field 'category' is invalid"}
    }


def test_E2S1_history_events_for_returns_routed_event(engine) -> None:
    clock = TestClock()
    ticket = create_ticket(
        engine,
        title="a",
        description="b",
        category="Billing",
        priority="High",
        customer_id="C-1",
        now=clock.now(),
    )
    assert history_events_for(engine, ticket.id) == ["ROUTED"]
