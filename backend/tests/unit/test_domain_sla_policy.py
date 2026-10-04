"""AC-10: SLA policy value rules (admin-console_spec.md). Pure validation,
no I/O. The float rejection itself happens at the API boundary (strict
pydantic ints); this module covers the cross-field and range rules.
"""

from __future__ import annotations

import pytest

from src.domain.sla_policy import validate_policy_minutes
from src.types.errors import ValidationError


def test_AC10_accepts_resolution_equal_to_response() -> None:
    validate_policy_minutes(response_minutes=45, resolution_minutes=45)


def test_AC10_accepts_resolution_greater_than_response() -> None:
    validate_policy_minutes(response_minutes=45, resolution_minutes=360)


def test_AC10_rejects_resolution_below_response() -> None:
    with pytest.raises(ValidationError) as exc:
        validate_policy_minutes(response_minutes=45, resolution_minutes=30)
    assert exc.value.field == "resolution_minutes"


def test_AC10_rejects_response_below_one() -> None:
    with pytest.raises(ValidationError) as exc:
        validate_policy_minutes(response_minutes=0, resolution_minutes=10)
    assert exc.value.field == "response_minutes"


def test_AC10_rejects_resolution_below_one() -> None:
    with pytest.raises(ValidationError) as exc:
        validate_policy_minutes(response_minutes=1, resolution_minutes=0)
    assert exc.value.field == "resolution_minutes"
