from __future__ import annotations

from fastapi.testclient import TestClient

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


def test_AC03_agent_detail_includes_assignments_oldest_first(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    agent1_headers = auth_header(client, "agent1")
    agent2_headers = auth_header(client, "agent2")

    client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent1_headers)
    client.post(
        f"/api/tickets/{ticket_id}/reassign",
        json={"assignee_id": "AG-2", "version": 2},
        headers=agent2_headers,
    )

    detail = client.get(f"/api/tickets/{ticket_id}", headers=agent1_headers)
    assert detail.status_code == 200
    assignments = detail.json()["assignments"]
    assert [(a["from_user_id"], a["to_user_id"], a["actor_id"]) for a in assignments] == [
        (None, "AG-1", "AG-1"),
        ("AG-1", "AG-2", "AG-2"),
    ]
    assert all(a["ticket_id"] == ticket_id for a in assignments)
    assert all(isinstance(a["id"], int) for a in assignments)
    assert all(a["created_at"] for a in assignments)


def test_AC03_customer_detail_never_receives_assignments(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    agent1_headers = auth_header(client, "agent1")
    client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent1_headers)

    customer_headers = auth_header(client, "customer1")
    detail = client.get(f"/api/tickets/{ticket_id}", headers=customer_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["assignments"] == []
    assert body["assignee_id"] == "AG-1"
