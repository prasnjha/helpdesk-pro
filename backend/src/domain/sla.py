"""Response and resolution timer math (sla-engine_spec.md, ASM-S6, NFR-01).

Integer minutes only: no float, no `/`, no `round()`, no `.total_seconds()`
(backend/src/domain/CLAUDE.md). No FastAPI or SQLAlchemy imports here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

ON_TRACK = "ON_TRACK"
AT_RISK = "AT_RISK"
BREACHED = "BREACHED"

_ONE_MINUTE = timedelta(minutes=1)


@dataclass(frozen=True)
class TimerSnapshot:
    target_minutes: int
    elapsed_minutes: int
    state: str
    stopped_at: datetime | None


@dataclass(frozen=True)
class SlaSnapshot:
    response: TimerSnapshot
    resolution: TimerSnapshot


def _elapsed_minutes(start: datetime, end: datetime) -> int:
    """Whole minutes between `start` and `end`, floor-divided. Never negative."""
    delta = end - start
    if delta < timedelta(0):
        return 0
    return delta // _ONE_MINUTE


def _state_for(elapsed_minutes: int, target_minutes: int) -> str:
    if elapsed_minutes >= target_minutes:
        return BREACHED
    if elapsed_minutes * 100 >= target_minutes * 80:
        return AT_RISK
    return ON_TRACK


def _evaluate_timer(
    *, created_at: datetime, now: datetime, target_minutes: int, stopped_at: datetime | None
) -> TimerSnapshot:
    end = stopped_at if stopped_at is not None else now
    elapsed = _elapsed_minutes(created_at, end)
    return TimerSnapshot(
        target_minutes=target_minutes,
        elapsed_minutes=elapsed,
        state=_state_for(elapsed, target_minutes),
        stopped_at=stopped_at,
    )


def evaluate_sla(
    *,
    created_at: datetime,
    now: datetime,
    response_target_minutes: int,
    resolution_target_minutes: int,
    response_stopped_at: datetime | None,
    resolution_stopped_at: datetime | None,
) -> SlaSnapshot:
    """Pure timer evaluation. Callers decide what to do with a BREACHED state
    (recording an SlaEvent and escalating is a service-layer concern).
    """
    response = _evaluate_timer(
        created_at=created_at,
        now=now,
        target_minutes=response_target_minutes,
        stopped_at=response_stopped_at,
    )
    resolution = _evaluate_timer(
        created_at=created_at,
        now=now,
        target_minutes=resolution_target_minutes,
        stopped_at=resolution_stopped_at,
    )
    return SlaSnapshot(response=response, resolution=resolution)


def breach_deadline(created_at: datetime, target_minutes: int) -> datetime:
    """The UTC deadline timestamp for a timer: `created_at` plus `target_minutes`."""
    return created_at + timedelta(minutes=target_minutes)
