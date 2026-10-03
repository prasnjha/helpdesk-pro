from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.api.app import create_app
from src.config.settings import get_settings
from src.repository.db import run_migrations
from src.types.clock import TestClock


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    settings = get_settings()
    run_migrations(eng, settings.migrations_dir)
    return eng


@pytest.fixture()
def clock() -> TestClock:
    return TestClock()


@pytest.fixture()
def app(engine, clock):
    return create_app(engine, clock)


@pytest.fixture()
def client(app):
    return TestClient(app)


def auth_header(
    client: TestClient, username: str, password: str = "Password123!"
) -> dict[str, str]:
    resp = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}
