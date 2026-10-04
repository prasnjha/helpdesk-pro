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


def test_NFR06_uvicorn_loggers_write_json_through_the_root_handler(
    log_stream: io.StringIO,
) -> None:
    _simulate_uvicorn_startup()
    try:
        configure_logging("INFO", stream=log_stream)

        logging.getLogger("uvicorn.error").info("Started server process")
        logging.getLogger("uvicorn.access").info(
            '%s - "%s %s HTTP/%s" %d', "127.0.0.1:5000", "GET", "/health", "1.1", 200
        )

        lines = [json.loads(line) for line in log_stream.getvalue().splitlines()]
        assert [line["logger"] for line in lines] == ["uvicorn.error", "uvicorn.access"]
        assert lines[1]["message"] == '127.0.0.1:5000 - "GET /health HTTP/1.1" 200'
    finally:
        _restore_uvicorn_loggers()


def test_NFR06_uvicorn_loggers_follow_the_configured_level(log_stream: io.StringIO) -> None:
    _simulate_uvicorn_startup()
    try:
        configure_logging("WARNING", stream=log_stream)

        logging.getLogger("uvicorn.access").info("quiet access line")
        logging.getLogger("uvicorn.error").warning("loud error line")

        lines = [json.loads(line) for line in log_stream.getvalue().splitlines()]
        assert [line["message"] for line in lines] == ["loud error line"]
    finally:
        _restore_uvicorn_loggers()
