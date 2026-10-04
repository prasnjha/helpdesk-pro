"""Admin SLA policy versioning orchestration (AC-10, admin-console_spec.md).
Published versions are immutable: PATCH, PUT and DELETE always refuse.
"""

from __future__ import annotations

from sqlalchemy import Engine

from src.domain.sla_policy import validate_policy_minutes
from src.repository import sla_policy_repository
from src.types.clock import Clock
from src.types.errors import PolicyVersionImmutableError
from src.types.models import SlaPolicyRecord


def create_version(
    engine: Engine,
    clock: Clock,
    *,
    priority: str,
    response_minutes: int,
    resolution_minutes: int,
    created_by: str,
) -> SlaPolicyRecord:
    validate_policy_minutes(
        response_minutes=response_minutes, resolution_minutes=resolution_minutes
    )
    with engine.begin() as conn:
        return sla_policy_repository.insert_version(
            conn,
            priority=priority,
            response_minutes=response_minutes,
            resolution_minutes=resolution_minutes,
            created_by=created_by,
            published_at=clock.now().isoformat(),
        )


def list_versions(engine: Engine, *, priority: str | None) -> list[SlaPolicyRecord]:
    with engine.connect() as conn:
        return sla_policy_repository.list_versions(conn, priority=priority)


def reject_mutation(engine: Engine, *, policy_id: int) -> None:
    """Always raise. Published SlaPolicy versions have no update or delete
    path (NFR-05); this function exists so the API layer has one call to
    make for PATCH, PUT and DELETE, and so no row is ever touched.
    """
    raise PolicyVersionImmutableError(f"SlaPolicy version '{policy_id}' is immutable")
