from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header

_UNKNOWN = "HD-999999"


def test_AC03_claim_unknown_ticket_returns_404(client: TestClient) -> None:
    headers = auth_header(client, "agent1")
    resp = client.post(f"/api/tickets/{_UNKNOWN}/claim", json={"version": 1}, headers=headers)
    assert resp.status_code == 404


def test_AC03_reassign_unknown_ticket_returns_404(client: TestClient) -> None:
    headers = auth_header(client, "agent1")
    resp = client.post(
        f"/api/tickets/{_UNKNOWN}/reassign",
        json={"assignee_id": "AG-2", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 404


def test_AC04_status_unknown_ticket_returns_404(client: TestClient) -> None:
    headers = auth_header(client, "agent1")
    resp = client.post(
        f"/api/tickets/{_UNKNOWN}/status",
        json={"to_status": "IN_PROGRESS", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 404


def test_AC07_note_on_unknown_ticket_returns_404(client: TestClient) -> None:
    headers = auth_header(client, "agent1")
    resp = client.post(
        f"/api/tickets/{_UNKNOWN}/notes", json={"body": "x"}, headers=headers
    )
    assert resp.status_code == 404


def test_AC08_reply_on_unknown_ticket_returns_404(client: TestClient) -> None:
    headers = auth_header(client, "customer1")
    resp = client.post(
        f"/api/tickets/{_UNKNOWN}/replies", json={"body": "x"}, headers=headers
    )
    assert resp.status_code == 404


def test_customer_detail_read_of_unknown_ticket_returns_404(client: TestClient) -> None:
    headers = auth_header(client, "customer1")
    resp = client.get(f"/api/tickets/{_UNKNOWN}", headers=headers)
    assert resp.status_code == 404
