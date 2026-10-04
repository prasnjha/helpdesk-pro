"""SLA policy value rules (admin-console_spec.md, AC-10).

No FastAPI or SQLAlchemy imports here (backend/src/domain/CLAUDE.md).
"""

from __future__ import annotations

from src.types.errors import ValidationError


def validate_policy_minutes(*, response_minutes: int, resolution_minutes: int) -> None:
    """Raise `ValidationError` unless both values are integers >= 1 and
    `resolution_minutes` is at least `response_minutes`.
    """
    if response_minutes < 1:
        raise ValidationError("response_minutes", "response_minutes must be at least 1")
    if resolution_minutes < 1:
        raise ValidationError("resolution_minutes", "resolution_minutes must be at least 1")
    if resolution_minutes < response_minutes:
        raise ValidationError(
            "resolution_minutes", "resolution_minutes must be >= response_minutes"
        )
