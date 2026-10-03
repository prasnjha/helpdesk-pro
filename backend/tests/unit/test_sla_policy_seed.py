from __future__ import annotations

from sqlalchemy import text

from src.config.settings import get_settings
from src.repository.db import run_migrations


def test_E1S4_exactly_four_v1_rows_one_per_priority(engine) -> None:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT priority, version FROM sla_policy")).all()
    assert len(rows) == 4
    assert {r[0] for r in rows} == {"Critical", "High", "Medium", "Low"}
    assert all(r[1] == 1 for r in rows)


def test_E1S4_seed_values_match_a10(engine) -> None:
    with engine.connect() as conn:
        rows = {
            r[0]: (r[1], r[2])
            for r in conn.execute(
                text("SELECT priority, response_minutes, resolution_minutes FROM sla_policy")
            ).all()
        }
    assert rows["Critical"] == (15, 240)
    assert rows["High"] == (60, 480)
    assert rows["Medium"] == (240, 1440)
    assert rows["Low"] == (480, 2880)


def test_E1S4_migration_applied_twice_keeps_row_count_at_four(engine) -> None:
    settings = get_settings()
    run_migrations(engine, settings.migrations_dir)  # re-apply; ledger should skip all files
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM sla_policy")).scalar_one()
    assert count == 4
