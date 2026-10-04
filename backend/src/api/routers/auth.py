"""POST /api/auth/login — no token required (E1-S2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import Engine

from src.api.deps import get_engine, get_token_store
from src.repository import user_repository
from src.repository.token_store import TokenStore
from src.service.auth_service import login as login_service

router = APIRouter(prefix="/api/auth")


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    # role/username let the UI route without a separate "/me" call (E6-S1/E6-S2
    # role-gated routing; additive field, api-contracts.md updated).
    role: str
    username: str


@router.post("/login", response_model=LoginResponse, status_code=200)
def login(
    payload: LoginRequest,
    engine: Engine = Depends(get_engine),
    token_store: TokenStore = Depends(get_token_store),
) -> LoginResponse:
    token = login_service(engine, token_store, payload.username, payload.password)
    with engine.connect() as conn:
        user = user_repository.get_by_username(conn, payload.username)
    assert user is not None  # login_service already validated the user exists and is active
    return LoginResponse(token=token, role=user.role, username=user.username)
