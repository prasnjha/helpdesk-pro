"""NFR-06: uvicorn's own loggers write JSON through the same handler as the app."""

from __future__ import annotations

import io
import json
import logging
import logging.config

from uvicorn.config import LOGGING_CONFIG

from src.config.logging_setup import configure_logging

UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")


def _simulate_uvicorn_startup() -> None:
    """Apply the logging config uvicorn installs before it imports the app."""
    logging.config.dictConfig(LOGGING_CONFIG)


def _restore_uvicorn_loggers() -> None:
    for name in UVICORN_LOGGERS:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(logging.NOTSET)


def _json_lines(stream: io.StringIO) -> list[dict[str, object]]:
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def test_NFR06_uvicorn_error_logger_writes_json_through_the_root_handler(
    log_stream: io.StringIO,
) -> None:
    _simulate_uvicorn_startup()
    try:
        configure_logging("INFO", stream=log_stream)

        logging.getLogger("uvicorn.error").info("Started server process")

        lines = _json_lines(log_stream)
        assert [line["logger"] for line in lines] == ["uvicorn.error"]
        assert lines[0]["message"] == "Started server process"
        assert lines[0]["level"] == "INFO"
    finally:
        _restore_uvicorn_loggers()


def test_NFR06_uvicorn_access_info_lines_are_replaced_by_the_request_line(
    log_stream: io.StringIO,
) -> None:
    """uvicorn's access line echoes the query string; helpdesk.request replaces it."""
    _simulate_uvicorn_startup()
    try:
        configure_logging("INFO", stream=log_stream)

        logging.getLogger("uvicorn.access").info(
            '%s - "%s %s HTTP/%s" %d', "127.0.0.1:5000", "GET", "/health?token=abc", "1.1", 200
        )

        assert log_stream.getvalue() == ""
    finally:
        _restore_uvicorn_loggers()


def test_NFR06_uvicorn_access_warnings_are_written_as_json(log_stream: io.StringIO) -> None:
    _simulate_uvicorn_startup()
    try:
        configure_logging("INFO", stream=log_stream)

        logging.getLogger("uvicorn.access").warning("access problem")

        lines = _json_lines(log_stream)
        assert [line["logger"] for line in lines] == ["uvicorn.access"]
        assert lines[0]["level"] == "WARNING"
    finally:
        _restore_uvicorn_loggers()


def test_NFR06_uvicorn_loggers_follow_the_configured_level(log_stream: io.StringIO) -> None:
    _simulate_uvicorn_startup()
    try:
        configure_logging("WARNING", stream=log_stream)

        logging.getLogger("uvicorn.error").info("quiet error line")
        logging.getLogger("uvicorn.error").warning("loud error line")

        lines = _json_lines(log_stream)
        assert [line["message"] for line in lines] == ["loud error line"]
    finally:
        _restore_uvicorn_loggers()
