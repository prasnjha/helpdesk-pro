from __future__ import annotations

import re

from fastapi.testclient import TestClient
from sqlalchemy import text

from tests.conftest import auth_header

VALID_PAYLOAD = {
    "title": "Invoice charged twice",
    "description": "I was billed twice for the same invoice.",
    "category": "Billing",
    "priority": "High",
}


def test_AC01_F001_create_ticket_returns_201_open_with_hd_id(client: TestClient) -> None:
    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "OPEN"
    assert re.match(r"^HD-\d{6}$", body["id"])
    assert body["customer_id"] == "C-1"


def test_AC01_F001_second_create_gets_a_new_never_reused_id(client: TestClient) -> None:
    headers = auth_header(client, "customer1")
    first = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers).json()
    second = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers).json()
    assert first["id"] != second["id"]


def test_AC01_F002_no_token_rejected_with_401_and_no_row_written(
    client: TestClient, engine
) -> None:
    resp = client.post("/api/tickets", json=VALID_PAYLOAD)
    assert resp.status_code == 401
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one()
    assert count == 0


def test_AC01_F002_invalid_category_rejected_with_422_validation_error(
    client: TestClient, engine
) -> None:
    headers = auth_header(client, "customer1")
    payload = {**VALID_PAYLOAD, "category": "Refunds"}
    resp = client.post("/api/tickets", json=payload, headers=headers)
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "category" in body["error"]["message"]
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one()
    assert count == 0


def test_AC01_F002_title_too_long_or_empty_description_rejected(client: TestClient) -> None:
    headers = auth_header(client, "customer1")
    too_long_title = {**VALID_PAYLOAD, "title": "x" * 201}
    resp = client.post("/api/tickets", json=too_long_title, headers=headers)
    assert resp.status_code == 422

    empty_description = {**VALID_PAYLOAD, "description": ""}
    resp = client.post("/api/tickets", json=empty_description, headers=headers)
    assert resp.status_code == 422


def test_AC02_F003_billing_technical_account_route_to_matching_queue_with_one_routed_row(
    client: TestClient, engine
) -> None:
    headers = auth_header(client, "customer1")
    for category in ("Billing", "Technical", "Account"):
        payload = {**VALID_PAYLOAD, "category": category}
        resp = client.post("/api/tickets", json=payload, headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["queue"]["name"] == category
        with engine.connect() as conn:
            history = conn.execute(
                text("SELECT event FROM ticket_history WHERE ticket_id = :id"),
                {"id": body["id"]},
            ).all()
        assert [row[0] for row in history] == ["ROUTED"]


def test_AC02_F004_missing_routing_rule_returns_409_and_writes_no_row(
    client: TestClient, engine
) -> None:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM routing_rules WHERE category = 'Billing'"))

    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "ROUTING_RULE_MISSING"
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM tickets")).scalar_one()
    assert count == 0


def test_AC01_customer_cannot_be_impersonated_other_roles_rejected(client: TestClient) -> None:
    headers = auth_header(client, "agent1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    assert resp.status_code == 403
