"""Stable error envelope: {"error": {"code", "message"}} (app_spec.md section 6)."""

from __future__ import annotations


class AppError(Exception):
    """Base class for every error that must cross the API boundary as an envelope."""

    status_code: int = 400
    code: str = "ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def to_envelope(self) -> dict[str, dict[str, str]]:
        return {"error": {"code": self.code, "message": self.message}}


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


class InvalidCredentialsError(AppError):
    status_code = 401
    code = "INVALID_CREDENTIALS"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class MethodNotAllowedError(AppError):
    status_code = 405
    code = "METHOD_NOT_ALLOWED"


class ValidationError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"

    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field


class VersionConflictError(AppError):
    status_code = 409
    code = "VERSION_CONFLICT"


class RoutingRuleMissingError(AppError):
    status_code = 409
    code = "ROUTING_RULE_MISSING"


class InvalidTicketStateError(AppError):
    status_code = 409
    code = "INVALID_TICKET_STATE"


class TicketClosedImmutableError(AppError):
    status_code = 409
    code = "TICKET_CLOSED_IMMUTABLE"


class SourceTicketNotResolvedError(AppError):
    status_code = 409
    code = "SOURCE_TICKET_NOT_RESOLVED"


class PolicyVersionImmutableError(AppError):
    status_code = 409
    code = "POLICY_VERSION_IMMUTABLE"
