"""NFR-03: email, phone and ticket body/description text are masked in log output.

All values below are synthetic (example.test domain, 555 and reserved numbers).
"""

from __future__ import annotations

import io
import json
import logging

import pytest

from src.config.log_redaction import REDACTED, RedactionFilter, redact_text
from src.config.logging_setup import configure_logging


@pytest.mark.parametrize(
    "text",
    [
        "+1 555-010-1234",
        "(555) 010-1234",
        "555.010.1234",
        "+44 20 7946 0958",
    ],
)
def test_NFR03_phone_numbers_are_masked(text: str) -> None:
    assert redact_text(f"Call {text} back") == "Call [REDACTED_PHONE] back"


def test_NFR03_email_addresses_are_masked() -> None:
    assert redact_text("Reply to jane.doe@example.test today") == "Reply to [REDACTED_EMAIL] today"


def test_NFR03_identifiers_and_timestamps_are_not_masked() -> None:
    text = "Ticket HD-000013 version 3 updated 2026-10-04T12:30:00Z by AG-2"
    assert redact_text(text) == text


def test_NFR03_filter_masks_ticket_body_and_description_fields() -> None:
    record = logging.makeLogRecord(
        {"msg": "ticket created", "body": "My card number is secret", "description": "x"}
    )

    RedactionFilter().filter(record)

    assert getattr(record, "body") == REDACTED
    assert getattr(record, "description") == REDACTED


def test_NFR03_filter_masks_pii_in_the_formatted_message() -> None:
    record = logging.makeLogRecord(
        {"msg": "notify %s at %s", "args": ("jane.doe@example.test", "+1 555-010-1234")}
    )

    RedactionFilter().filter(record)

    assert record.getMessage() == "notify [REDACTED_EMAIL] at [REDACTED_PHONE]"


def test_NFR03_pii_never_reaches_json_log_output(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)

    logging.getLogger("helpdesk.test").info(
        "Customer jane.doe@example.test called +1 555-010-1234",
        extra={"body": "Call me on +1 555-010-1234 about the invoice"},
    )

    output = log_stream.getvalue()
    assert "jane.doe@example.test" not in output
    assert "555-010-1234" not in output
    assert "invoice" not in output
    record = json.loads(output)
    assert record["message"] == "Customer [REDACTED_EMAIL] called [REDACTED_PHONE]"
