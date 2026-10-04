"""Reads for GET /api/admin/dashboard (admin-console_spec.md). Read-only:
no inserts or updates.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Engine, text

from src.types.models import QueueRef


def open_counts_by_queue(engine: Engine) -> list[tuple[QueueRef, int]]:
    """Count tickets per queue whose status is not RESOLVED or CLOSED."""
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT t.slug AS slug, t.name AS name, "
                    "SUM(CASE WHEN k.status NOT IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END) "
                    "AS cnt "
                    "FROM teams t LEFT JOIN tickets k ON k.queue_id = t.id "
                    "GROUP BY t.id ORDER BY t.slug"
                )
            )
            .mappings()
            .all()
        )
        return [
            (QueueRef(slug=row["slug"], name=row["name"]), int(row["cnt"] or 0)) for row in rows
        ]


def breach_events_in_range(
    engine: Engine, *, start: datetime, end: datetime
) -> list[tuple[str, datetime]]:
    """Return (priority, breached_at) for every BREACHED_* event, for the
    caller to filter by range. Timestamps are parsed here so the caller
    compares real `datetime` values rather than raw ISO strings.
    """
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT t.priority AS priority, se.breached_at AS breached_at "
                    "FROM sla_event se JOIN tickets t ON t.id = se.ticket_id "
                    "WHERE se.event IN ('BREACHED_RESPONSE', 'BREACHED_RESOLUTION')"
                )
            )
            .mappings()
            .all()
        )
    result = []
    for row in rows:
        breached_at = datetime.fromisoformat(row["breached_at"])
        if start <= breached_at <= end:
            result.append((row["priority"], breached_at))
    return result


def escalation_count_in_range(engine: Engine, *, start: datetime, end: datetime) -> int:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT created_at FROM sla_event WHERE event = 'ESCALATED'")
        ).all()
    count = 0
    for (created_at,) in rows:
        if start <= datetime.fromisoformat(created_at) <= end:
            count += 1
    return count
