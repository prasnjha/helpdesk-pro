"""Admin SLA policy versioning endpoints (AC-10, api-contracts.md).

Published versions are immutable: PATCH, PUT and DELETE always return 409.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import Engine

from src.api.deps import get_clock, get_engine, require_role
from src.service.sla_policy_service import create_version, list_versions, reject_mutation
from src.types.clock import Clock
from src.types.models import SlaPolicyRecord, UserRecord

router = APIRouter(prefix="/api/admin/sla-policies")


class CreatePolicyRequest(BaseModel):
    priority: Literal["Critical", "High", "Medium", "Low"]
    response_minutes: int = Field(strict=True)
    resolution_minutes: int = Field(strict=True)


class PolicyOut(BaseModel):
    id: int
    priority: str
    version: int
    response_minutes: int
    resolution_minutes: int
    created_by: str
    published_at: str


def _policy_out(record: SlaPolicyRecord) -> PolicyOut:
    return PolicyOut(
        id=record.id,
        priority=record.priority,
        version=record.version,
        response_minutes=record.response_minutes,
        resolution_minutes=record.resolution_minutes,
        created_by=record.created_by,
        published_at=record.published_at,
    )


@router.post("", response_model=PolicyOut, status_code=201)
def create_policy(
    payload: CreatePolicyRequest,
    engine: Engine = Depends(get_engine),
    clock: Clock = Depends(get_clock),
    user: UserRecord = Depends(require_role("admin")),
) -> PolicyOut:
    record = create_version(
        engine,
        clock,
        priority=payload.priority,
        response_minutes=payload.response_minutes,
        resolution_minutes=payload.resolution_minutes,
        created_by=user.id,
    )
    return _policy_out(record)


@router.get("", response_model=list[PolicyOut])
def list_policies(
    priority: Literal["Critical", "High", "Medium", "Low"] | None = None,
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(require_role("admin")),
) -> list[PolicyOut]:
    return [_policy_out(record) for record in list_versions(engine, priority=priority)]


@router.patch("/versions/{policy_id}")
@router.put("/versions/{policy_id}")
@router.delete("/versions/{policy_id}")
def mutate_policy_version(
    policy_id: int,
    engine: Engine = Depends(get_engine),
    user: UserRecord = Depends(require_role("admin")),
) -> None:
    reject_mutation(engine, policy_id=policy_id)
