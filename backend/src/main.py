"""Production entry point: `uv run uvicorn src.main:app --port 8000`."""

from __future__ import annotations

from src.api.app import create_app
from src.config.settings import get_settings
from src.repository.db import make_engine, run_migrations
from src.types.clock import SystemClock

settings = get_settings()
engine = make_engine(settings)
run_migrations(engine, settings.migrations_dir)

app = create_app(engine, SystemClock(), settings.cors_allowed_origins)
