from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header

VALID_PAYLOAD = {
    "title": "Invoice charged twice",
    "description": "I was billed twice for the same invoice.",
    "category": "Billing",
    "priority": "High",
}


def test_E2S4_list_tickets_returns_only_own_tickets(client: TestClient) -> None:
    headers = auth_header(client, "customer1")
    created = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers).json()

    resp = client.get("/api/tickets", headers=headers)
    assert resp.status_code == 200
    ids = [t["id"] for t in resp.json()]
    assert created["id"] in ids


def test_E2S4_list_tickets_without_token_returns_401(client: TestClient) -> None:
    resp = client.get("/api/tickets")
    assert resp.status_code == 401
