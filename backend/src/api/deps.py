"""Shared FastAPI dependencies: engine/clock/token access, auth, role checks."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header, Request
from sqlalchemy import Engine

from src.repository.token_store import TokenStore
from src.service.auth_service import current_user
from src.types.clock import Clock
from src.types.errors import ForbiddenError, UnauthorizedError
from src.types.models import UserRecord


def get_engine(request: Request) -> Engine:
    engine: Engine = request.app.state.engine
    return engine


def get_clock(request: Request) -> Clock:
    clock: Clock = request.app.state.clock
    return clock


def get_token_store(request: Request) -> TokenStore:
    store: TokenStore = request.app.state.token_store
    return store


def get_current_user(
    request: Request, authorization: str | None = Header(default=None)
) -> UserRecord:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    user = current_user(request.app.state.engine, request.app.state.token_store, token)
    if user is None or not user.active:
        raise UnauthorizedError("Invalid or expired token")
    return user


def require_role(*roles: str) -> Callable[[UserRecord], UserRecord]:
    def checker(user: UserRecord = Depends(get_current_user)) -> UserRecord:
        if user.role not in roles:
            raise ForbiddenError(f"Role '{user.role}' may not perform this action")
        return user

    return checker
