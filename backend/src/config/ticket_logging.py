"""The one way ticket text reaches a log line (NFR-03).

Subject and body are redacted before formatting and the body is truncated, so
raw ticket content never appears in log output.
"""

from __future__ import annotations

import logging

from src.config.log_redaction import redact_text

MAX_LOGGED_BODY_CHARS = 200


def log_ticket_content(
    logger: logging.Logger,
    level: int,
    event: str,
    *,
    ticket_id: str,
    subject: str,
    body: str,
) -> None:
    safe_subject = redact_text(subject)
    safe_body = redact_text(body)[:MAX_LOGGED_BODY_CHARS]
    logger.log(
        level,
        "%s: ticket=%s subject=%s body=%s",
        event,
        ticket_id,
        safe_subject,
        safe_body,
    )
