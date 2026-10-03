"""AC-04: any write to a CLOSED ticket other than a status transition returns 409
TICKET_CLOSED_IMMUTABLE (ticket-lifecycle_spec.md, agent-workbench_spec.md).
"""

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


def _create_closed_ticket(client: TestClient, engine) -> str:
    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    ticket_id: str = resp.json()["id"]
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tickets SET status = 'CLOSED' WHERE id = :id"), {"id": ticket_id}
        )
    return ticket_id


def test_AC04_claim_on_closed_ticket_returns_409_ticket_closed_immutable(
    client: TestClient, engine
) -> None:
    ticket_id = _create_closed_ticket(client, engine)
    headers = auth_header(client, "agent1")

    resp = client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=headers)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "TICKET_CLOSED_IMMUTABLE"


def test_AC04_reassign_on_closed_ticket_returns_409_ticket_closed_immutable(
    client: TestClient, engine
) -> None:
    ticket_id = _create_closed_ticket(client, engine)
    headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/reassign",
        json={"assignee_id": "AG-2", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "TICKET_CLOSED_IMMUTABLE"


def test_AC04_note_on_closed_ticket_returns_409_ticket_closed_immutable(
    client: TestClient, engine
) -> None:
    ticket_id = _create_closed_ticket(client, engine)
    headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/notes", json={"body": "x"}, headers=headers
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "TICKET_CLOSED_IMMUTABLE"


def test_AC07_agent_reply_on_closed_ticket_returns_409_ticket_closed_immutable(
    client: TestClient, engine
) -> None:
    ticket_id = _create_closed_ticket(client, engine)
    headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/replies", json={"body": "x"}, headers=headers
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "TICKET_CLOSED_IMMUTABLE"
