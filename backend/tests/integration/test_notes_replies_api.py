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


def test_AC07_F013_agent_note_returns_201_and_never_appears_to_customer(
    client: TestClient,
) -> None:
    ticket_id = _create_ticket(client)
    agent_headers = auth_header(client, "agent1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={"body": "Checked refund log"},
        headers=agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["body"] == "Checked refund log"

    customer_headers = auth_header(client, "customer1")
    detail = client.get(f"/api/tickets/{ticket_id}", headers=customer_headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert "notes" not in detail_body or detail_body["notes"] == []
    assert "Checked refund log" not in detail.text

    customer_reply = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "Any update?"},
        headers=customer_headers,
    )
    assert "Checked refund log" not in customer_reply.text

    customer_list = client.get("/api/tickets", headers=customer_headers)
    assert "Checked refund log" not in customer_list.text


def test_AC07_F014_put_patch_delete_on_note_or_reply_id_return_405_and_change_no_row(
    client: TestClient, engine
) -> None:
    ticket_id = _create_ticket(client)
    agent_headers = auth_header(client, "agent1")

    note = client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={"body": "Checked refund log"},
        headers=agent_headers,
    )
    note_id = note.json()["id"]
    reply = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "We are checking this now."},
        headers=agent_headers,
    )
    reply_id = reply.json()["id"]

    for method in ("put", "patch", "delete"):
        resp = getattr(client, method)(
            f"/api/tickets/{ticket_id}/notes/{note_id}", headers=agent_headers
        )
        assert resp.status_code == 405
        assert resp.json()["error"]["code"] == "METHOD_NOT_ALLOWED"

        resp = getattr(client, method)(
            f"/api/tickets/{ticket_id}/replies/{reply_id}", headers=agent_headers
        )
        assert resp.status_code == 405
        assert resp.json()["error"]["code"] == "METHOD_NOT_ALLOWED"

    with engine.connect() as conn:
        note_body = conn.execute(
            text("SELECT body FROM ticket_notes WHERE id = :id"), {"id": note_id}
        ).scalar_one()
        reply_body = conn.execute(
            text("SELECT body FROM ticket_replies WHERE id = :id"), {"id": reply_id}
        ).scalar_one()
    assert note_body == "Checked refund log"
    assert reply_body == "We are checking this now."


def test_AC07_agent_public_reply_is_visible_to_the_customer(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    agent_headers = auth_header(client, "agent1")
    customer_headers = auth_header(client, "customer1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/replies",
        json={"body": "We are checking this now."},
        headers=agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["author_role"] == "agent"

    detail = client.get(f"/api/tickets/{ticket_id}", headers=customer_headers)
    assert detail.status_code == 200
    bodies = [r["body"] for r in detail.json()["replies"]]
    assert "We are checking this now." in bodies


def test_AC07_agent_detail_view_includes_notes_history_and_replies(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    agent_headers = auth_header(client, "agent1")

    client.post(
        f"/api/tickets/{ticket_id}/notes",
        json={"body": "Checked refund log"},
        headers=agent_headers,
    )
    client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=agent_headers)

    detail = client.get(f"/api/tickets/{ticket_id}", headers=agent_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert [n["body"] for n in body["notes"]] == ["Checked refund log"]
    assert [h["event"] for h in body["history"]] == ["ROUTED", "STATUS_CHANGED"]


def test_AC07_customer_calling_notes_endpoint_returns_403(client: TestClient) -> None:
    ticket_id = _create_ticket(client)
    headers = auth_header(client, "customer1")

    resp = client.post(
        f"/api/tickets/{ticket_id}/notes", json={"body": "Should not work"}, headers=headers
    )
    assert resp.status_code == 403
