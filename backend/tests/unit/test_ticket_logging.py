"""NFR-03: ticket subject and body are logged only through the redaction path."""

from __future__ import annotations

import io
import json
import logging

from src.config.logging_setup import configure_logging
from src.config.ticket_logging import MAX_LOGGED_BODY_CHARS, log_ticket_content


def test_NFR03_log_ticket_content_redacts_subject_and_body(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)

    log_ticket_content(
        logging.getLogger("helpdesk.tickets"),
        logging.INFO,
        "ticket created",
        ticket_id="HD-000001",
        subject="Refund for jane.doe@example.test",
        body="Hi Jordan Blake, call +1 555-010-1234 about the invoice.",
    )

    output = log_stream.getvalue()
    assert "jane.doe@example.test" not in output
    assert "555-010-1234" not in output
    assert "Jordan Blake" not in output
    record = json.loads(output)
    assert record["logger"] == "helpdesk.tickets"
    assert "HD-000001" in record["message"]
    assert "[REDACTED_EMAIL]" in record["message"]
    assert "[REDACTED_PHONE]" in record["message"]
    assert "[REDACTED_NAME]" in record["message"]


def test_NFR03_log_ticket_content_truncates_the_body(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)

    log_ticket_content(
        logging.getLogger("helpdesk.tickets"),
        logging.INFO,
        "ticket created",
        ticket_id="HD-000002",
        subject="Long body",
        body="x" * (MAX_LOGGED_BODY_CHARS + 50),
    )

    message = str(json.loads(log_stream.getvalue())["message"])
    assert "x" * MAX_LOGGED_BODY_CHARS in message
    assert "x" * (MAX_LOGGED_BODY_CHARS + 1) not in message
