"""NFR-06: the log level is read from configuration (LOG_LEVEL), defaulting to INFO."""

from __future__ import annotations

import pytest

from src.config.settings import get_settings


def test_NFR06_log_level_defaults_to_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    assert get_settings().log_level == "INFO"


def test_NFR06_log_level_is_read_from_environment_and_normalised(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "warning")

    assert get_settings().log_level == "WARNING"
