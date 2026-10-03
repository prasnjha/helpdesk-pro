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

_SIX_VALID_EDGES = [
    ("OPEN", "IN_PROGRESS"),
    ("IN_PROGRESS", "PENDING_CUSTOMER"),
    ("PENDING_CUSTOMER", "RESOLVED"),
    ("RESOLVED", "CLOSED"),
    ("PENDING_CUSTOMER", "OPEN"),
    ("IN_PROGRESS", "RESOLVED"),
]


def _create_ticket(client: TestClient) -> str:
    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    ticket_id: str = resp.json()["id"]
    return ticket_id


def _set_status_directly(engine, ticket_id: str, status: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tickets SET status = :status WHERE id = :id"),
            {"status": status, "id": ticket_id},
        )


def test_AC04_F007_each_of_the_six_valid_edges_returns_200_and_writes_one_history_row(
    client: TestClient, engine
) -> None:
    headers = auth_header(client, "agent1")
    for from_state, to_state in _SIX_VALID_EDGES:
        ticket_id = _create_ticket(client)
        _set_status_directly(engine, ticket_id, from_state)
        with engine.connect() as conn:
            version = conn.execute(
                text("SELECT version FROM tickets WHERE id = :id"), {"id": ticket_id}
            ).scalar_one()

        resp = client.post(
            f"/api/tickets/{ticket_id}/status",
            json={"to_status": to_state, "version": version},
            headers=headers,
        )
        assert resp.status_code == 200, (from_state, to_state, resp.json())
        assert resp.json()["status"] == to_state

        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT from_state, to_state, actor_id FROM ticket_history "
                    "WHERE ticket_id = :id AND event = 'STATUS_CHANGED'"
                ),
                {"id": ticket_id},
            ).all()
        assert len(rows) == 1
        assert rows[0][0] == from_state
        assert rows[0][1] == to_state
        assert rows[0][2] == "AG-1"


def test_AC04_F008_open_to_resolved_returns_409_invalid_state_status_unchanged(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"to_status": "RESOLVED", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "INVALID_TICKET_STATE"

    with engine.connect() as conn:
        status = conn.execute(
            text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
        ).scalar_one()
        history_count = conn.execute(
            text(
                "SELECT COUNT(*) FROM ticket_history "
                "WHERE ticket_id = :id AND event = 'STATUS_CHANGED'"
            ),
            {"id": ticket_id},
        ).scalar_one()
    assert status == "OPEN"
    assert history_count == 0


def test_AC04_closed_ticket_any_transition_returns_409_invalid_state(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    _set_status_directly(engine, ticket_id, "CLOSED")
    headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"to_status": "OPEN", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "INVALID_TICKET_STATE"


def test_AC04_customer_calling_status_endpoint_returns_403(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "customer1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"to_status": "IN_PROGRESS", "version": 1},
        headers=headers,
    )
    assert resp.status_code == 403
