"""AC-06, AC-10: pure escalation and policy-validation rules
(escalation_spec.md, admin-console_spec.md). No I/O in this module.
"""

from __future__ import annotations

from src.domain.escalation import tier2_slug_for


def test_AC06_tier2_slug_for_billing() -> None:
    assert tier2_slug_for("billing") == "billing-tier-2"


def test_AC06_tier2_slug_for_technical() -> None:
    assert tier2_slug_for("technical") == "technical-tier-2"


def test_AC06_tier2_slug_for_account() -> None:
    assert tier2_slug_for("account") == "account-tier-2"


def test_AC06_tier2_slug_is_idempotent_for_an_already_tier2_queue() -> None:
    # A ticket already in Tier 2 (second breach) must not be routed further.
    assert tier2_slug_for("billing-tier-2") == "billing-tier-2"
