"""AC-05: GET /api/tickets/{id}/sla (api-contracts.md SLA read)."""

from __future__ import annotations

from tests.conftest import auth_header


def _create_ticket(client, *, priority: str = "Critical", category: str = "Billing") -> str:
    headers = auth_header(client, "customer1")
    resp = client.post(
        "/api/tickets",
        json={
            "title": "t",
            "description": "d",
            "category": category,
            "priority": priority,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return str(resp.json()["id"])


def test_AC05_on_track_then_at_risk_then_breached(client, clock) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "customer1")

    clock.advance(11)
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["response"]["state"] == "ON_TRACK"

    clock.advance(1)  # 12 minutes
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=headers)
    assert resp.json()["response"]["state"] == "AT_RISK"

    clock.advance(3)  # 15 minutes
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=headers)
    assert resp.json()["response"]["state"] == "BREACHED"


def test_AC05_customer_cannot_read_another_customers_ticket_timer(client) -> None:
    ticket_id = _create_ticket(client)
    other = auth_header(client, "customer2")
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=other)
    assert resp.status_code == 404


def test_AC05_agent_can_read_any_tickets_timer(client) -> None:
    ticket_id = _create_ticket(client)
    agent = auth_header(client, "agent1")
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=agent)
    assert resp.status_code == 200


def test_AC05_unauthenticated_request_is_401(client) -> None:
    ticket_id = _create_ticket(client)
    resp = client.get(f"/api/tickets/{ticket_id}/sla")
    assert resp.status_code == 401


def test_AC05_unknown_ticket_is_404(client) -> None:
    agent = auth_header(client, "agent1")
    resp = client.get("/api/tickets/HD-999999/sla", headers=agent)
    assert resp.status_code == 404


def test_AC06_response_breach_escalates_ticket_to_tier_2(client, clock) -> None:
    ticket_id = _create_ticket(client)
    clock.advance(15)
    agent = auth_header(client, "agent1")
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=agent)
    assert resp.status_code == 200
    detail = client.get(f"/api/tickets/{ticket_id}", headers=agent)
    body = detail.json()
    assert body["escalated"] is True
    assert body["status"] == "OPEN"
    assert body["queue"]["slug"] == "billing-tier-2"


def test_AC06_repeat_read_writes_no_new_escalation_history_row(client, clock) -> None:
    ticket_id = _create_ticket(client)
    clock.advance(15)
    agent = auth_header(client, "agent1")
    client.get(f"/api/tickets/{ticket_id}/sla", headers=agent)
    clock.advance(5)
    client.get(f"/api/tickets/{ticket_id}/sla", headers=agent)
    detail = client.get(f"/api/tickets/{ticket_id}", headers=agent).json()
    escalated_events = [h for h in detail["history"] if h["event"] == "ESCALATED"]
    assert len(escalated_events) == 1


def test_AC05_internal_note_does_not_stop_response_timer_via_api(client, clock) -> None:
    ticket_id = _create_ticket(client)
    agent = auth_header(client, "agent1")
    clock.advance(5)
    client.post(f"/api/tickets/{ticket_id}/notes", json={"body": "looking into it"}, headers=agent)
    clock.advance(20)
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=agent)
    assert resp.json()["response"]["state"] == "BREACHED"


def test_AC05_public_reply_stops_response_timer(client, clock) -> None:
    ticket_id = _create_ticket(client)
    agent = auth_header(client, "agent1")
    clock.advance(5)
    client.post(f"/api/tickets/{ticket_id}/notes", json={"body": "note"}, headers=agent)
    clock.advance(15)  # total +20
    client.post(f"/api/tickets/{ticket_id}/replies", json={"body": "we are on it"}, headers=agent)
    clock.advance(25)
    resp = client.get(f"/api/tickets/{ticket_id}/sla", headers=agent)
    body = resp.json()["response"]
    assert body["elapsed_minutes"] == 20
    assert body["stopped_at"] is not None
