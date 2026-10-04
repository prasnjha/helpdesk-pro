"""Knowledge base value rules (api-contracts.md, AC-09).

No FastAPI or SQLAlchemy imports here (backend/src/domain/CLAUDE.md).
"""

from __future__ import annotations

from src.types.errors import ValidationError

_MAX_TAGS = 10
_MAX_TAG_LENGTH = 30


def validate_tags(tags: list[str]) -> None:
    """Raise `ValidationError` unless `tags` has 1 to 10 entries, each a
    lowercase string of 1 to 30 characters.
    """
    if not 1 <= len(tags) <= _MAX_TAGS:
        raise ValidationError("tags", "tags must have between 1 and 10 entries")
    for tag in tags:
        if not 1 <= len(tag) <= _MAX_TAG_LENGTH:
            raise ValidationError("tags", f"tag '{tag}' must be 1 to 30 characters")
        if tag != tag.lower():
            raise ValidationError("tags", f"tag '{tag}' must be lowercase")
