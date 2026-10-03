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


def _set_status_directly(engine, ticket_id: str, status: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tickets SET status = :status WHERE id = :id"),
            {"status": status, "id": ticket_id},
        )


def test_AC08_F015_reply_on_pending_customer_returns_201_moves_to_open_one_history_row(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    _set_status_directly(engine, ticket_id, "PENDING_CUSTOMER")
    headers = auth_header(client, "customer1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "Attached the invoice."},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "OPEN"

    with engine.connect() as conn:
        status = conn.execute(
            text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
        ).scalar_one()
        rows = conn.execute(
            text(
                "SELECT from_state, to_state FROM ticket_history "
                "WHERE ticket_id = :id AND event = 'STATUS_CHANGED'"
            ),
            {"id": ticket_id},
        ).all()
        reply_count = conn.execute(
            text("SELECT COUNT(*) FROM ticket_replies WHERE ticket_id = :id"), {"id": ticket_id}
        ).scalar_one()
    assert status == "OPEN"
    assert len(rows) == 1
    assert rows[0][0] == "PENDING_CUSTOMER"
    assert rows[0][1] == "OPEN"
    assert reply_count == 1


def test_AC08_F016_reply_on_resolved_returns_409_invalid_state_no_reply_written(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    _set_status_directly(engine, ticket_id, "RESOLVED")
    headers = auth_header(client, "customer1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "Still waiting"},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "INVALID_TICKET_STATE"

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM ticket_replies WHERE ticket_id = :id"), {"id": ticket_id}
        ).scalar_one()
    assert count == 0


def test_AC08_reply_on_closed_returns_409_invalid_state_no_reply_written(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    _set_status_directly(engine, ticket_id, "CLOSED")
    headers = auth_header(client, "customer1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "Still waiting"},
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "INVALID_TICKET_STATE"

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM ticket_replies WHERE ticket_id = :id"), {"id": ticket_id}
        ).scalar_one()
    assert count == 0


def test_AC08_reply_on_open_or_in_progress_keeps_status_unchanged(
    client: TestClient, engine
) -> None:
    headers = auth_header(client, "customer1")
    for status in ("OPEN", "IN_PROGRESS"):
        ticket_id = _create_ticket(client)
        _set_status_directly(engine, ticket_id, status)

        resp = client.post(
            f"/api/tickets/{ticket_id}/replies", json={"body": "Here's more info"}, headers=headers
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == status


def test_AC08_reply_by_non_owner_customer_returns_404_and_writes_no_row(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    other_customer_headers = auth_header(client, "customer2")

    resp = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "Not my ticket"},
        headers=other_customer_headers,
    )
    assert resp.status_code == 404

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM ticket_replies WHERE ticket_id = :id"), {"id": ticket_id}
        ).scalar_one()
    assert count == 0
