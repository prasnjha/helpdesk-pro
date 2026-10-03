"""User reads. Users are seeded; no create/update path in Group A."""

from __future__ import annotations

from sqlalchemy import Connection, Engine, text

from src.types.models import UserRecord


def get_by_username(conn: Connection, username: str) -> UserRecord | None:
    row = conn.execute(
        text(
            "SELECT id, username, password_hash, role, team_id, active "
            "FROM users WHERE username = :username"
        ),
        {"username": username},
    ).mappings().first()
    if row is None:
        return None
    return UserRecord(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        role=row["role"],
        team_id=row["team_id"],
        active=bool(row["active"]),
    )


def get_by_id_via_engine(engine: Engine, user_id: str) -> UserRecord | None:
    with engine.connect() as conn:
        return get_by_id(conn, user_id)


def get_by_id(conn: Connection, user_id: str) -> UserRecord | None:
    row = conn.execute(
        text(
            "SELECT id, username, password_hash, role, team_id, active "
            "FROM users WHERE id = :id"
        ),
        {"id": user_id},
    ).mappings().first()
    if row is None:
        return None
    return UserRecord(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        role=row["role"],
        team_id=row["team_id"],
        active=bool(row["active"]),
    )
