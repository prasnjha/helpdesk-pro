"""App configuration (env vars, constants). No I/O beyond reading the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    migrations_dir: str
    cors_allowed_origins: list[str]
    log_level: str


def get_settings() -> Settings:
    default_db = os.path.join(os.path.dirname(__file__), "..", "..", "helpdesk.db")
    database_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.abspath(default_db)}")
    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "repository", "migrations")
    default_origins = "http://localhost:5173,http://127.0.0.1:5173"
    cors_allowed_origins = [
        origin.strip()
        for origin in os.environ.get("CORS_ALLOWED_ORIGINS", default_origins).split(",")
        if origin.strip()
    ]
    return Settings(
        database_url=database_url,
        migrations_dir=os.path.abspath(migrations_dir),
        cors_allowed_origins=cors_allowed_origins,
        log_level=os.environ.get("LOG_LEVEL", "INFO").strip().upper() or "INFO",
    )
