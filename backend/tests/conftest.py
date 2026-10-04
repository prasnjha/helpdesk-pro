from __future__ import annotations

import io
import logging
from collections.abc import Iterator

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
def log_stream() -> Iterator[io.StringIO]:
    """Capture JSON log output in memory and restore the root logger afterwards."""
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    stream = io.StringIO()
    yield stream
    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)


@pytest.fixture()
def app(engine, clock):
    settings = get_settings()
    return create_app(engine, clock, settings.cors_allowed_origins)


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
