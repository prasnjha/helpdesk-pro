"""Login: verify seeded credentials, issue a bearer token (E1-S2)."""

from __future__ import annotations

from sqlalchemy import Engine

from src.repository import user_repository
from src.repository.security import verify_password
from src.repository.token_store import TokenStore
from src.types.errors import InvalidCredentialsError
from src.types.models import UserRecord


def login(engine: Engine, token_store: TokenStore, username: str, password: str) -> str:
    with engine.connect() as conn:
        user = user_repository.get_by_username(conn, username)
    if user is None or not user.active or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Incorrect username or password")
    return token_store.issue(user.id)


def current_user(engine: Engine, token_store: TokenStore, token: str) -> UserRecord | None:
    user_id = token_store.resolve(token)
    if user_id is None:
        return None
    with engine.connect() as conn:
        return user_repository.get_by_id(conn, user_id)
