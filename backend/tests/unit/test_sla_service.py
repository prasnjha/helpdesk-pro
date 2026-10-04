"""Service-layer wiring for AC-05 (sla read) and AC-10 (policy admin)."""

from __future__ import annotations

import pytest

from src.service import sla_policy_service, sla_service
from src.types.clock import TestClock
from src.types.errors import NotFoundError, PolicyVersionImmutableError, ValidationError


def _ticket(engine, clock: TestClock, customer_id: str = "C-1"):
    from src.repository import ticket_repository

    return ticket_repository.create_ticket(
        engine,
        title="t",
        description="d",
        category="Billing",
        priority="Critical",
        customer_id=customer_id,
        now=clock.now(),
    )


def test_AC05_get_snapshot_for_customer_owner(engine) -> None:
    clock = TestClock()
    ticket = _ticket(engine, clock)
    clock.advance(10)
    out = sla_service.get_snapshot_for_customer(engine, clock, ticket.id, "C-1")
    assert out.response.elapsed_minutes == 10


def test_AC05_get_snapshot_for_customer_not_owner_is_not_found(engine) -> None:
    clock = TestClock()
    ticket = _ticket(engine, clock, customer_id="C-1")
    with pytest.raises(NotFoundError):
        sla_service.get_snapshot_for_customer(engine, clock, ticket.id, "C-2")


def test_AC05_get_snapshot_for_agent_unknown_ticket_is_not_found(engine) -> None:
    clock = TestClock()
    with pytest.raises(NotFoundError):
        sla_service.get_snapshot_for_agent(engine, clock, "HD-999999")


def test_AC10_create_version_rejects_resolution_below_response(engine) -> None:
    clock = TestClock()
    with pytest.raises(ValidationError):
        sla_policy_service.create_version(
            engine,
            clock,
            priority="High",
            response_minutes=100,
            resolution_minutes=50,
            created_by="AD-1",
        )


def test_AC10_create_version_returns_version_2(engine) -> None:
    clock = TestClock()
    record = sla_policy_service.create_version(
        engine,
        clock,
        priority="High",
        response_minutes=45,
        resolution_minutes=360,
        created_by="AD-1",
    )
    assert record.version == 2


def test_AC10_reject_mutation_of_published_version(engine) -> None:
    with pytest.raises(PolicyVersionImmutableError):
        sla_policy_service.reject_mutation(engine, policy_id=1)
