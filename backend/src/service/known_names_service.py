"""Loads user display names into the log redaction registry (NFR-03).

Call after startup migrations, and again after any user row is added or renamed.
"""

from __future__ import annotations

from sqlalchemy import Engine

from src.config.log_redaction import known_names
from src.repository import user_repository


def refresh_known_names(engine: Engine) -> None:
    with engine.connect() as conn:
        known_names.replace(user_repository.list_display_names(conn))
