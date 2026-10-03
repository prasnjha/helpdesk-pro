from __future__ import annotations

import pytest

from src.domain.routing import resolve_queue_id
from src.types.errors import RoutingRuleMissingError


def test_AC02_resolve_queue_id_returns_mapped_queue() -> None:
    assert resolve_queue_id("Billing", {"Billing": 1, "Technical": 2}) == 1


def test_AC02_resolve_queue_id_raises_when_rule_missing() -> None:
    with pytest.raises(RoutingRuleMissingError):
        resolve_queue_id("Billing", {})
