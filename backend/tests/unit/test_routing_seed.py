from __future__ import annotations

from sqlalchemy import text

from src.repository import routing_repository


def test_E2S2_each_category_has_exactly_one_rule_to_same_name_team(engine) -> None:
    with engine.connect() as conn:
        rules = routing_repository.get_all_rules(conn)
        for category in ("Billing", "Technical", "Account"):
            team_name = conn.execute(
                text("SELECT name FROM teams WHERE id = :id"), {"id": rules[category]}
            ).scalar_one()
            assert team_name == category


def test_E2S2_tier_2_teams_exist(engine) -> None:
    with engine.connect() as conn:
        slugs = {
            r[0]
            for r in conn.execute(text("SELECT slug FROM teams")).all()
        }
    assert {"billing-tier-2", "technical-tier-2", "account-tier-2"}.issubset(slugs)
