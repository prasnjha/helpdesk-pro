from __future__ import annotations

from fastapi.testclient import TestClient


def test_E1S2_login_with_correct_password_returns_token(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/login", json={"username": "customer1", "password": "Password123!"}
    )
    assert resp.status_code == 200
    assert resp.json()["token"]


def test_E6S1_login_response_includes_role_and_username_for_ui_routing(
    client: TestClient,
) -> None:
    resp = client.post(
        "/api/auth/login", json={"username": "agent1", "password": "Password123!"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "agent"
    assert body["username"] == "agent1"


def test_E1S2_login_with_wrong_password_returns_401_invalid_credentials(
    client: TestClient,
) -> None:
    resp = client.post("/api/auth/login", json={"username": "customer1", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert "token" not in resp.json()


def test_E1S2_protected_route_without_token_returns_401(client: TestClient) -> None:
    resp = client.post(
        "/api/tickets",
        json={
            "title": "x",
            "description": "y",
            "category": "Billing",
            "priority": "High",
        },
    )
    assert resp.status_code == 401
