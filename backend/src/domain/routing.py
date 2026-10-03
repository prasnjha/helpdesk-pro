"""Pure routing rule: category -> target queue id (routing_spec.md).

No FastAPI or SQLAlchemy imports here (backend/src/domain/CLAUDE.md).
"""

from __future__ import annotations

from src.types.errors import RoutingRuleMissingError


def resolve_queue_id(category: str, rules: dict[str, int]) -> int:
    """Return the target queue id for `category`, or raise if no rule exists.

    `rules` is a plain mapping built by the repository from the current
    RoutingRule rows. This function holds no state and performs no I/O.
    """
    if category not in rules:
        raise RoutingRuleMissingError(f"No routing rule for category '{category}'")
    return rules[category]
