from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import text

from tests.conftest import auth_header

VALID_PAYLOAD = {
    "title": "Invoice charged twice",
    "description": "I was billed twice for the same invoice.",
    "category": "Billing",
    "priority": "High",
}


def _create_ticket(client: TestClient) -> str:
    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    ticket_id: str = resp.json()["id"]
    return ticket_id


def test_AC03_F005_claim_open_ticket_sets_assignee_and_moves_to_in_progress(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "agent1")

    resp = client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["assignee_id"] == "AG-1"
    assert body["status"] == "IN_PROGRESS"

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT from_user_id, to_user_id, actor_id FROM assignments WHERE ticket_id = :id"
            ),
            {"id": ticket_id},
        ).all()
    assert len(rows) == 1
    assert rows[0][0] is None
    assert rows[0][1] == "AG-1"
    assert rows[0][2] == "AG-1"


def test_AC03_F006_reassign_changes_assignee_keeps_status_appends_second_row(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    agent1_headers = auth_header(client, "agent1")
    agent2_headers = auth_header(client, "agent2")

    client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent1_headers)

    resp = client.post(
        f"/api/tickets/{ticket_id}/reassign",
        json={"assignee_id": "AG-2", "version": 2},
        headers=agent2_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "IN_PROGRESS"
    assert body["assignee_id"] == "AG-2"

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT from_user_id, to_user_id FROM assignments "
                "WHERE ticket_id = :id ORDER BY id"
            ),
            {"id": ticket_id},
        ).all()
    assert len(rows) == 2
    assert rows[1][0] == "AG-1"
    assert rows[1][1] == "AG-2"


def test_AC03_customer_claim_returns_403_and_writes_no_row(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "customer1")

    resp = client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=headers)
    assert resp.status_code == 403

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM assignments WHERE ticket_id = :id"), {"id": ticket_id}
        ).scalar_one()
    assert count == 0


def test_AC03_stale_version_claim_returns_409_version_conflict(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    agent1_headers = auth_header(client, "agent1")
    agent2_headers = auth_header(client, "agent2")

    first = client.post(
        f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent1_headers
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent2_headers
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "VERSION_CONFLICT"


def test_AC03_reassign_target_must_be_an_active_agent(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/reassign",
        json={"assignee_id": "C-1", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
