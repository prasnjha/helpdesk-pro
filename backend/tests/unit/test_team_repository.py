from __future__ import annotations

from src.repository import team_repository


def test_E2S2_get_by_slug_returns_queue_ref(engine) -> None:
    with engine.connect() as conn:
        queue = team_repository.get_by_slug(conn, "billing")
    assert queue is not None
    assert queue.slug == "billing"
    assert queue.name == "Billing"


def test_E2S2_get_by_slug_returns_none_for_unknown_slug(engine) -> None:
    with engine.connect() as conn:
        queue = team_repository.get_by_slug(conn, "nonexistent")
    assert queue is None


def test_E2S2_get_by_id_returns_none_for_unknown_id(engine) -> None:
    with engine.connect() as conn:
        queue = team_repository.get_by_id(conn, 999999)
    assert queue is None
