"""Tier-2 queue routing rule (escalation_spec.md, A-05, A-06).

No FastAPI or SQLAlchemy imports here (backend/src/domain/CLAUDE.md).
"""

from __future__ import annotations

_TIER2_SUFFIX = "-tier-2"


def tier2_slug_for(queue_slug: str) -> str:
    """Return the tier-2 slug for `queue_slug`. A queue already in tier 2 maps
    to itself, so re-escalating an already-escalated ticket is a no-op move.
    """
    if queue_slug.endswith(_TIER2_SUFFIX):
        return queue_slug
    return f"{queue_slug}{_TIER2_SUFFIX}"
