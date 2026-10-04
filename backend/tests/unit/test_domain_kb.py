"""AC-09: knowledge base tag value rules (domain/kb.py)."""

from __future__ import annotations

import pytest

from src.domain.kb import validate_tags
from src.types.errors import ValidationError


def test_AC09_one_to_ten_lowercase_tags_are_accepted() -> None:
    validate_tags(["billing", "invoice"])


def test_AC09_empty_tags_list_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_tags([])


def test_AC09_more_than_ten_tags_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_tags([f"tag{i}" for i in range(11)])


def test_AC09_uppercase_tag_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_tags(["Billing"])


def test_AC09_tag_longer_than_30_chars_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_tags(["a" * 31])


def test_AC09_empty_string_tag_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_tags([""])
