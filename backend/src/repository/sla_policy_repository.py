"""SlaPolicy reads. Append-only: insert and read only, no update/delete (E1-S4)."""

from __future__ import annotations

from sqlalchemy import Connection, text


def get_active_version_id(conn: Connection, priority: str) -> int | None:
    """Return the id of the highest (newest) published version for `priority`."""
    row = conn.execute(
        text(
            "SELECT id FROM sla_policy WHERE priority = :priority "
            "ORDER BY version DESC LIMIT 1"
        ),
        {"priority": priority},
    ).first()
    return None if row is None else int(row[0])
