"""RoutingRule reads (routing_spec.md). Rules are plain rows, not versioned (A-07)."""

from __future__ import annotations

from sqlalchemy import Connection, text


def get_all_rules(conn: Connection) -> dict[str, int]:
    rows = conn.execute(text("SELECT category, target_queue_id FROM routing_rules")).all()
    return {row[0]: row[1] for row in rows}
