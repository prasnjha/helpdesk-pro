"""AC-04 logging: the closed-ticket rejection is logged at the configured level,
with the request's correlation id (ticket-lifecycle_spec.md, NFR-06).
"""

from __future__ import annotations

import io
import json

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.config.logging_setup import configure_logging
from tests.conftest import auth_header

VALID_PAYLOAD = {
    "title": "Invoice charged twice",
    "description": "I was billed twice for the same invoice.",
    "category": "Billing",
    "priority": "High",
}
REJECTION_MESSAGE = "Rejected write to CLOSED ticket"


def _create_closed_ticket(client: TestClient, engine) -> str:
    headers = auth_header(client, "customer1")
    resp = client.post("/api/tickets", json=VALID_PAYLOAD, headers=headers)
    ticket_id: str = resp.json()["id"]
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tickets SET status = 'CLOSED' WHERE id = :id"), {"id": ticket_id}
        )
    return ticket_id


def _rejection_records(stream: io.StringIO) -> list[dict[str, object]]:
    records = [json.loads(line) for line in stream.getvalue().splitlines() if line]
    return [r for r in records if REJECTION_MESSAGE in str(r["message"])]


def test_AC04_closed_ticket_rejection_is_logged_at_info_with_correlation_id(
    client: TestClient, engine, log_stream: io.StringIO
) -> None:
    ticket_id = _create_closed_ticket(client, engine)
    configure_logging("INFO", stream=log_stream)
    headers = {**auth_header(client, "agent1"), "X-Correlation-Id": "closed-write-001"}

    resp = client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=headers)

    assert resp.status_code == 409
    records = _rejection_records(log_stream)
    assert len(records) == 1
    assert records[0]["level"] == "INFO"
    assert records[0]["logger"] == "helpdesk.closed_ticket_writes"
    assert records[0]["correlation_id"] == "closed-write-001"


def test_AC04_closed_ticket_rejection_is_suppressed_when_level_is_above_info(
    client: TestClient, engine, log_stream: io.StringIO
) -> None:
    ticket_id = _create_closed_ticket(client, engine)
    configure_logging("WARNING", stream=log_stream)
    headers = auth_header(client, "agent1")

    resp = client.post(f"/api/tickets/{ticket_id}/claim", json={"version": 1}, headers=headers)

    assert resp.status_code == 409
    assert _rejection_records(log_stream) == []
