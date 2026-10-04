"""SlaPolicy reads and version inserts. Append-only: insert and read only, no
update/delete (E1-S4, E4-S1). Published versions are immutable (AC-10).
"""

from __future__ import annotations

from sqlalchemy import Connection, text

from src.types.models import SlaPolicyRecord


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


def _next_version(conn: Connection, priority: str) -> int:
    row = conn.execute(
        text("SELECT MAX(version) FROM sla_policy WHERE priority = :priority"),
        {"priority": priority},
    ).first()
    current = row[0] if row is not None else None
    return 1 if current is None else int(current) + 1


def insert_version(
    conn: Connection,
    *,
    priority: str,
    response_minutes: int,
    resolution_minutes: int,
    created_by: str,
    published_at: str,
) -> SlaPolicyRecord:
    """Insert a new published version for `priority`. Earlier versions are
    never touched (AC-10): this is an insert, never an update.
    """
    version = _next_version(conn, priority)
    result = conn.execute(
        text(
            "INSERT INTO sla_policy "
            "(priority, version, response_minutes, resolution_minutes, created_by, published_at) "
            "VALUES (:priority, :version, :response_minutes, :resolution_minutes, "
            ":created_by, :published_at)"
        ),
        {
            "priority": priority,
            "version": version,
            "response_minutes": response_minutes,
            "resolution_minutes": resolution_minutes,
            "created_by": created_by,
            "published_at": published_at,
        },
    )
    new_id = result.lastrowid
    assert new_id is not None
    return SlaPolicyRecord(
        id=int(new_id),
        priority=priority,
        version=version,
        response_minutes=response_minutes,
        resolution_minutes=resolution_minutes,
        created_by=created_by,
        published_at=published_at,
    )


def get_by_id(conn: Connection, policy_id: int) -> SlaPolicyRecord | None:
    row = (
        conn.execute(text("SELECT * FROM sla_policy WHERE id = :id"), {"id": policy_id})
        .mappings()
        .first()
    )
    if row is None:
        return None
    return SlaPolicyRecord(**row)


def list_versions(conn: Connection, *, priority: str | None) -> list[SlaPolicyRecord]:
    """All versions, newest first. `priority` narrows to one priority."""
    if priority is None:
        rows = (
            conn.execute(text("SELECT * FROM sla_policy ORDER BY priority, version DESC"))
            .mappings()
            .all()
        )
    else:
        rows = (
            conn.execute(
                text(
                    "SELECT * FROM sla_policy WHERE priority = :priority "
                    "ORDER BY version DESC"
                ),
                {"priority": priority},
            )
            .mappings()
            .all()
        )
    return [SlaPolicyRecord(**row) for row in rows]


def get_targets(conn: Connection, policy_id: int) -> tuple[int, int]:
    """Return `(response_minutes, resolution_minutes)` for `policy_id`."""
    row = conn.execute(
        text("SELECT response_minutes, resolution_minutes FROM sla_policy WHERE id = :id"),
        {"id": policy_id},
    ).first()
    assert row is not None, f"SlaPolicy id {policy_id} not found"
    return int(row[0]), int(row[1])
