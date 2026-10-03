from __future__ import annotations

from src.repository import user_repository
from src.repository.token_store import TokenStore
from src.service.auth_service import current_user


def test_E1S2_get_by_id_returns_none_for_unknown_user(engine) -> None:
    with engine.connect() as conn:
        assert user_repository.get_by_id(conn, "nope") is None


def test_E1S2_current_user_returns_none_for_unknown_token(engine) -> None:
    store = TokenStore()
    assert current_user(engine, store, "not-a-real-token") is None
