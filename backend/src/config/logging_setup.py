"""Structured JSON logging configured once at startup (NFR-06).

Each log line is one JSON object: timestamp, level, logger, message, correlation_id,
plus any structured fields a caller passes in `json_fields`. The correlation id comes
from a context variable that the API middleware sets per request. uvicorn's own
loggers are routed through the same root handler.
"""

from __future__ import annotations

import json
import logging
import sys
import traceback
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import TextIO

from src.config.log_redaction import RedactionFilter, redact_text

HANDLER_NAME = "helpdesk-json"
UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
        }
        fields = getattr(record, "json_fields", None)
        if isinstance(fields, dict):
            for key, value in fields.items():
                payload.setdefault(str(key), value)
        if record.exc_info:
            payload["exception"] = redact_text(
                "".join(traceback.format_exception(*record.exc_info))
            )
        return json.dumps(payload, ensure_ascii=False)


def _route_uvicorn_loggers() -> None:
    """Send uvicorn's loggers to the root JSON handler and follow the root level.

    uvicorn.access INFO lines echo the raw query string, so they are held at WARNING;
    the helpdesk.request line (no query string, plus correlation id) replaces them.
    """
    for name in UVICORN_LOGGERS:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def configure_logging(level: str, stream: TextIO | None = None) -> None:
    """Install the JSON handler on the root logger at `level`. Safe to call repeatedly."""
    numeric_level = logging.getLevelNamesMapping().get(level.upper())
    if numeric_level is None:
        raise ValueError(f"Unknown log level: {level}")

    root = logging.getLogger()
    for existing in [h for h in root.handlers if h.get_name() == HANDLER_NAME]:
        root.removeHandler(existing)

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.set_name(HANDLER_NAME)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(CorrelationIdFilter())
    handler.addFilter(RedactionFilter())
    root.addHandler(handler)
    root.setLevel(numeric_level)
    _route_uvicorn_loggers()
