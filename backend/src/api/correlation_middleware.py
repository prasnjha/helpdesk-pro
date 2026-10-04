"""Correlation id and request log line per HTTP request (NFR-06).

Reuses a well-formed incoming X-Correlation-Id, otherwise generates one. The id is
stored in a context variable so every log line written during the request carries
it, and it is returned in the X-Correlation-Id response header. Each request also
writes one `helpdesk.request` line with method, path (no query string), status and
duration_ms. Request and response bodies are never read or logged.
"""

from __future__ import annotations

import logging
import re
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.config.log_redaction import redact_text
from src.config.logging_setup import correlation_id_var

CORRELATION_HEADER = "X-Correlation-Id"
REQUEST_LOGGER = "helpdesk.request"
_HEADER_KEY = b"x-correlation-id"
_SAFE_ID = re.compile(r"[A-Za-z0-9._:-]{1,128}")
_request_log = logging.getLogger(REQUEST_LOGGER)


def resolve_correlation_id(incoming: str | None) -> str:
    if incoming is not None and _SAFE_ID.fullmatch(incoming):
        return incoming
    return uuid.uuid4().hex


def _incoming_header(scope: Scope) -> str | None:
    for name, value in scope.get("headers", []):
        if name == _HEADER_KEY:
            return bytes(value).decode("latin-1")
    return None


def _log_request(scope: Scope, status_code: int, started: float) -> None:
    duration_ms = int((time.perf_counter() - started) * 1000)
    _request_log.info(
        "request completed",
        extra={
            "json_fields": {
                "method": scope["method"],
                "path": redact_text(scope["path"]),
                "status": status_code,
                "duration_ms": duration_ms,
            }
        },
    )


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        correlation_id = resolve_correlation_id(_incoming_header(scope))
        started = time.perf_counter()
        status_code = 500

        async def send_with_header(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                MutableHeaders(scope=message)[CORRELATION_HEADER] = correlation_id
            await send(message)

        token = correlation_id_var.set(correlation_id)
        try:
            await self.app(scope, receive, send_with_header)
        finally:
            _log_request(scope, status_code, started)
            correlation_id_var.reset(token)
