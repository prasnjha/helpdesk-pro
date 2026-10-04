from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header

VALID_PAYLOAD = {
    "title": "Invoice charged twice",
    "description": "I was billed twice for the same invoice.",
    "category": "Billing",
    "priority": "High",
}


def _create_ticket(client: TestClient, *, category: str = "Billing", priority: str = "High") -> str:
    headers = auth_header(client, "customer1")
    payload = {**VALID_PAYLOAD, "category": category, "priority": priority}
    resp = client.post("/api/tickets", json=payload, headers=headers)
    ticket_id: str = resp.json()["id"]
    return ticket_id


def test_F021_agent_lists_tickets_in_own_queue(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    agent_headers = auth_header(client, "agent1")

    resp = client.get("/api/agent/queues/billing/tickets", headers=agent_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert any(row["id"] == ticket_id for row in body)
    row = next(row for row in body if row["id"] == ticket_id)
    assert row["priority"] == "High"
    assert row["status"] == "OPEN"
    assert row["queue"] == {"slug": "billing", "name": "Billing"}
    assert row["assignee_id"] is None
    assert row["escalated"] is False
    assert row["response_state"] == "ON_TRACK"
    assert row["resolution_state"] == "ON_TRACK"


def test_F021_queue_excludes_tickets_from_other_queues(client: TestClient) -> None:
    _create_ticket(client, category="Technical")
    agent_headers = auth_header(client, "agent1")

    resp = client.get("/api/agent/queues/billing/tickets", headers=agent_headers)

    assert resp.status_code == 200
    assert all(row["category"] if "category" in row else True for row in resp.json())
    # only billing tickets returned: none have queue slug other than billing
    assert all(row["queue"]["slug"] == "billing" for row in resp.json())


def test_F021_filters_by_priority_status_and_escalated(client: TestClient) -> None:
    high_id = _create_ticket(client, priority="High")
    low_id = _create_ticket(client, priority="Low")
    agent_headers = auth_header(client, "agent1")

    resp = client.get(
        "/api/agent/queues/billing/tickets", params={"priority": "High"}, headers=agent_headers
    )

    ids = {row["id"] for row in resp.json()}
    assert high_id in ids
    assert low_id not in ids

    resp = client.get(
        "/api/agent/queues/billing/tickets", params={"status": "OPEN"}, headers=agent_headers
    )
    assert all(row["status"] == "OPEN" for row in resp.json())

    resp = client.get(
        "/api/agent/queues/billing/tickets", params={"escalated": "false"}, headers=agent_headers
    )
    assert all(row["escalated"] is False for row in resp.json())


def test_F022_customer_forbidden_from_queue_endpoint(client: TestClient) -> None:
    _create_ticket(client)
    customer_headers = auth_header(client, "customer1")

    resp = client.get("/api/agent/queues/billing/tickets", headers=customer_headers)

    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_F022_unknown_queue_slug_returns_404(client: TestClient) -> None:
    agent_headers = auth_header(client, "agent1")

    resp = client.get("/api/agent/queues/not-a-real-queue/tickets", headers=agent_headers)

    assert resp.status_code == 404


def test_F021_admin_may_also_list_queue_tickets(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    admin_headers = auth_header(client, "admin1")

    resp = client.get("/api/agent/queues/billing/tickets", headers=admin_headers)

    assert resp.status_code == 200
    assert any(row["id"] == ticket_id for row in resp.json())
