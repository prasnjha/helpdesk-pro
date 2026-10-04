"""Production entry point: `uv run uvicorn src.main:app --port 8000`."""

from __future__ import annotations

from src.api.app import create_app
from src.config.logging_setup import configure_logging
from src.config.settings import get_settings
from src.repository.db import make_engine, run_migrations
from src.types.clock import SystemClock

settings = get_settings()
configure_logging(settings.log_level)
engine = make_engine(settings)
run_migrations(engine, settings.migrations_dir)

app = create_app(engine, SystemClock(), settings.cors_allowed_origins)
