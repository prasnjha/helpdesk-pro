"""AC-05: response and resolution timer math (sla-engine_spec.md, ASM-S6).

Worked examples from the sla-policy-evaluator skill. All arithmetic is
integer-minute only; this module never sleeps and never touches a database.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from src.domain.sla import evaluate_sla


def _at(minutes: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=minutes)


T0 = datetime(2026, 1, 1, tzinfo=UTC)


def test_AC05_critical_on_track_at_11_minutes() -> None:
    snap = evaluate_sla(
        created_at=T0,
        now=_at(11),
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.response.elapsed_minutes == 11
    assert snap.response.state == "ON_TRACK"


def test_AC05_critical_at_risk_at_12_minutes() -> None:
    snap = evaluate_sla(
        created_at=T0,
        now=_at(12),
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.response.state == "AT_RISK"


def test_AC05_critical_at_risk_at_14_minutes_59_seconds() -> None:
    now = T0 + timedelta(minutes=14, seconds=59)
    snap = evaluate_sla(
        created_at=T0,
        now=now,
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.response.elapsed_minutes == 14
    assert snap.response.state == "AT_RISK"


def test_AC05_critical_breached_at_15_minutes() -> None:
    snap = evaluate_sla(
        created_at=T0,
        now=_at(15),
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.response.state == "BREACHED"


def test_AC05_response_stops_at_first_public_reply_not_internal_note() -> None:
    # Internal note at +5 min does not stop the timer; the reply at +20 min does.
    stopped_at = _at(20)
    snap = evaluate_sla(
        created_at=T0,
        now=_at(45),
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=stopped_at,
        resolution_stopped_at=None,
    )
    assert snap.response.elapsed_minutes == 20
    assert snap.response.stopped_at == stopped_at


def test_AC05_pending_customer_resolution_timer_keeps_running() -> None:
    snap = evaluate_sla(
        created_at=T0,
        now=_at(300),
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=_at(5),
        resolution_stopped_at=None,
    )
    assert snap.resolution.elapsed_minutes == 300
    assert snap.resolution.stopped_at is None


def test_AC05_resolution_stops_at_resolved_and_stays_fixed() -> None:
    stopped_at = _at(200)
    snap = evaluate_sla(
        created_at=T0,
        now=_at(500),
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=_at(5),
        resolution_stopped_at=stopped_at,
    )
    assert snap.resolution.elapsed_minutes == 200
    assert snap.resolution.stopped_at == stopped_at


def test_AC05_elapsed_minutes_never_goes_negative_if_now_precedes_created_at() -> None:
    # Defensive: clock skew or a bad input should never produce a negative
    # elapsed value (NFR-01 is integers only, never negative here).
    snap = evaluate_sla(
        created_at=_at(10),
        now=T0,
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.response.elapsed_minutes == 0
    assert snap.response.state == "ON_TRACK"


def test_AC05_high_priority_on_track_at_14_minutes_of_60_target() -> None:
    snap = evaluate_sla(
        created_at=T0,
        now=_at(14),
        response_target_minutes=60,
        resolution_target_minutes=480,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.response.state == "ON_TRACK"


@pytest.mark.parametrize("elapsed", [0, 1, 239])
def test_AC05_elapsed_minutes_uses_integer_floor_division_never_float(elapsed: int) -> None:
    now = T0 + timedelta(minutes=elapsed, seconds=59)
    snap = evaluate_sla(
        created_at=T0,
        now=now,
        response_target_minutes=15,
        resolution_target_minutes=240,
        response_stopped_at=None,
        resolution_stopped_at=None,
    )
    assert snap.resolution.elapsed_minutes == elapsed
    assert isinstance(snap.resolution.elapsed_minutes, int)
