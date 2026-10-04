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


def test_F023_dashboard_reports_open_tickets_by_queue(client: TestClient) -> None:
    ticket_id = _create_ticket(client, category="Billing")
    admin_headers = auth_header(client, "admin1")

    resp = client.get(
        "/api/admin/dashboard",
        params={"from": "2026-01-01", "to": "2026-01-31"},
        headers=admin_headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    billing_row = next(row for row in body["open_by_queue"] if row["queue"]["slug"] == "billing")
    assert billing_row["count"] >= 1
    assert "breached_by_priority" in body
    assert isinstance(body["escalations_in_period"], int)
    assert ticket_id  # the ticket exists and is counted above


def test_F023_dashboard_counts_breaches_and_escalations_in_period(
    client: TestClient, engine, clock
) -> None:
    ticket_id = _create_ticket(client, priority="High")
    agent_headers = auth_header(client, "agent1")
    client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent_headers)
    clock.advance(61)  # High response target is 60 minutes (seed policy)

    # Reading the SLA snapshot evaluates the timers and records the breach/escalation.
    client.get(f"/api/tickets/{ticket_id}/sla", headers=agent_headers)

    admin_headers = auth_header(client, "admin1")
    resp = client.get(
        "/api/admin/dashboard",
        params={"from": "2026-01-01", "to": "2026-01-02"},
        headers=admin_headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    high_row = next(
        (row for row in body["breached_by_priority"] if row["priority"] == "High"), None
    )
    assert high_row is not None
    assert high_row["count"] >= 1
    assert body["escalations_in_period"] >= 1


def test_F023_dashboard_forbidden_for_non_admin(client: TestClient) -> None:
    agent_headers = auth_header(client, "agent1")

    resp = client.get(
        "/api/admin/dashboard",
        params={"from": "2026-01-01", "to": "2026-01-31"},
        headers=agent_headers,
    )

    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_F023_dashboard_bad_date_range_returns_422(client: TestClient) -> None:
    admin_headers = auth_header(client, "admin1")

    resp = client.get(
        "/api/admin/dashboard",
        params={"from": "2026-02-01", "to": "2026-01-01"},
        headers=admin_headers,
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_F023_dashboard_invalid_date_format_returns_422(client: TestClient) -> None:
    admin_headers = auth_header(client, "admin1")

    resp = client.get(
        "/api/admin/dashboard",
        params={"from": "not-a-date", "to": "2026-01-31"},
        headers=admin_headers,
    )

    assert resp.status_code == 422
