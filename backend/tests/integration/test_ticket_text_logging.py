"""NFR-03: a ticket with an email, phone number and names in its text never leaks them into logs."""

from __future__ import annotations

import io
import json

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from src.config.logging_setup import configure_logging
from src.service.known_names_service import refresh_known_names
from tests.conftest import auth_header

PII_PAYLOAD = {
    "title": "Refund for jane.doe@example.test",
    "description": (
        "Hi Jordan Blake, my name is Jordan Blake. Reach me at jane.doe@example.test "
        "or +1 555-010-1234. Priya Raman also asked about this invoice."
    ),
    "category": "Billing",
    "priority": "High",
}
LEAKED_VALUES = [
    "jane.doe@example.test",
    "555-010-1234",
    "Jordan Blake",
    "Priya Raman",
]


def test_NFR03_ticket_create_logs_no_email_phone_or_name(
    client: TestClient, engine: Engine, log_stream: io.StringIO
) -> None:
    refresh_known_names(engine)
    configure_logging("INFO", stream=log_stream)

    resp = client.post(
        "/api/tickets", json=PII_PAYLOAD, headers=auth_header(client, "customer1")
    )

    assert resp.status_code == 201
    output = log_stream.getvalue()
    for value in LEAKED_VALUES:
        assert value not in output
    created = [
        json.loads(line)
        for line in output.splitlines()
        if "ticket created" in json.loads(line)["message"]
    ]
    assert len(created) == 1
    assert "[REDACTED_EMAIL]" in created[0]["message"]
