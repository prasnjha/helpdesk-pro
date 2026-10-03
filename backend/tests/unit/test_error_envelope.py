from __future__ import annotations

from fastapi.testclient import TestClient


def test_E1S1_error_body_has_exactly_code_and_message(client: TestClient) -> None:
    resp = client.post("/api/auth/login", json={"username": "nobody", "password": "wrong"})
    assert resp.status_code == 401
    body = resp.json()
    assert set(body.keys()) == {"error"}
    assert set(body["error"].keys()) == {"code", "message"}
    assert body["error"]["code"] == "INVALID_CREDENTIALS"
