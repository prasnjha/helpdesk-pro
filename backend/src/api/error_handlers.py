"""Exception -> error envelope mapping (app_spec.md section 6)."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.types.errors import AppError, TicketClosedImmutableError

logger = logging.getLogger("helpdesk.closed_ticket_writes")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        if isinstance(exc, TicketClosedImmutableError):
            # correlation_id is added to the JSON line by the logging filter.
            logger.info("Rejected write to CLOSED ticket: %s", exc.message)
        return JSONResponse(status_code=exc.status_code, content=exc.to_envelope())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        field = "body"
        if errors:
            loc = [str(part) for part in errors[0]["loc"] if part != "body"]
            field = loc[-1] if loc else "body"
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Field '{field}' is invalid",
                }
            },
        )
