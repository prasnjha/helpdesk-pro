"""In-memory bearer token store, scoped to the running process."""

from __future__ import annotations

import secrets


class TokenStore:
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def issue(self, user_id: str) -> str:
        token = secrets.token_hex(32)
        self._tokens[token] = user_id
        return token

    def resolve(self, token: str) -> str | None:
        return self._tokens.get(token)
