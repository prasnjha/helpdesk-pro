"""X-Correlation-Id middleware (NFR-06).

Reuses a well-formed incoming id, otherwise generates one. The id is stored in a
context variable so every log line written during the request carries it, and it
is returned in the X-Correlation-Id response header.
"""

from __future__ import annotations

import re
import uuid

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.config.logging_setup import correlation_id_var

CORRELATION_HEADER = "X-Correlation-Id"
_HEADER_KEY = b"x-correlation-id"
_SAFE_ID = re.compile(r"[A-Za-z0-9._:-]{1,128}")


def resolve_correlation_id(incoming: str | None) -> str:
    if incoming is not None and _SAFE_ID.fullmatch(incoming):
        return incoming
    return uuid.uuid4().hex


def _incoming_header(scope: Scope) -> str | None:
    for name, value in scope.get("headers", []):
        if name == _HEADER_KEY:
            return bytes(value).decode("latin-1")
    return None


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        correlation_id = resolve_correlation_id(_incoming_header(scope))

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[CORRELATION_HEADER] = correlation_id
            await send(message)

        token = correlation_id_var.set(correlation_id)
        try:
            await self.app(scope, receive, send_with_header)
        finally:
            correlation_id_var.reset(token)
