"""GET /api/admin/dashboard orchestration (admin-console_spec.md).

`open_by_queue` is a live snapshot of currently-open tickets (not time
scoped); `breached_by_priority` and `escalations_in_period` are counted
over the `[from, to]` window, per the endpoint's `from`/`to` query params.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, time

from sqlalchemy import Engine

from src.repository import dashboard_repository
from src.types.errors import ValidationError
from src.types.models import QueueRef


@dataclass(frozen=True)
class DashboardReport:
    open_by_queue: list[tuple[QueueRef, int]]
    breached_by_priority: list[tuple[str, int]]
    escalations_in_period: int


def get_dashboard(engine: Engine, *, from_date: date, to_date: date) -> DashboardReport:
    if from_date > to_date:
        raise ValidationError("to", "'to' must not be before 'from'")

    start = datetime.combine(from_date, time.min, tzinfo=UTC)
    end = datetime.combine(to_date, time.max, tzinfo=UTC)

    open_by_queue = dashboard_repository.open_counts_by_queue(engine)
    breaches = dashboard_repository.breach_events_in_range(engine, start=start, end=end)
    tally = Counter(priority for priority, _ in breaches)
    breached_by_priority = sorted(tally.items())
    escalations = dashboard_repository.escalation_count_in_range(engine, start=start, end=end)

    return DashboardReport(
        open_by_queue=open_by_queue,
        breached_by_priority=breached_by_priority,
        escalations_in_period=escalations,
    )
