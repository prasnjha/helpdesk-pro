"""Team (queue) reads."""

from __future__ import annotations

from sqlalchemy import Connection, text

from src.types.models import QueueRef


def get_by_id(conn: Connection, team_id: int) -> QueueRef | None:
    row = conn.execute(
        text("SELECT slug, name FROM teams WHERE id = :id"), {"id": team_id}
    ).mappings().first()
    if row is None:
        return None
    return QueueRef(slug=row["slug"], name=row["name"])


def get_by_slug(conn: Connection, slug: str) -> QueueRef | None:
    row = conn.execute(
        text("SELECT slug, name FROM teams WHERE slug = :slug"), {"slug": slug}
    ).mappings().first()
    if row is None:
        return None
    return QueueRef(slug=row["slug"], name=row["name"])
