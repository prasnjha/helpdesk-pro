"""PII redaction for log output (NFR-03).

Masks email addresses and phone numbers in log messages, and masks ticket
body/description values attached to a record. Stdlib only, so the config
layer stays free of upward imports.
"""

from __future__ import annotations

import logging
import re

REDACTED = "[REDACTED]"
REDACTED_EMAIL = "[REDACTED_EMAIL]"
REDACTED_PHONE = "[REDACTED_PHONE]"

SENSITIVE_FIELDS = frozenset({"body", "description", "ticket_body", "ticket_description"})

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Candidate phone: optional +, then digits with common separators. The digit count
# is checked separately so short numbers and dates are left alone.
_PHONE_CANDIDATE = re.compile(r"(?<![\w+])\(?\+?\d(?:[\s().-]{0,2}\d){8,14}(?!\w)")
_MIN_PHONE_DIGITS = 10
_MAX_PHONE_DIGITS = 15


def _mask_phone(match: re.Match[str]) -> str:
    digits = sum(ch.isdigit() for ch in match.group(0))
    if _MIN_PHONE_DIGITS <= digits <= _MAX_PHONE_DIGITS:
        return REDACTED_PHONE
    return match.group(0)


def redact_text(text: str) -> str:
    masked = _EMAIL.sub(REDACTED_EMAIL, text)
    return _PHONE_CANDIDATE.sub(_mask_phone, masked)


class RedactionFilter(logging.Filter):
    """Masks PII in the formatted message and in sensitive record attributes."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage())
        record.args = ()
        for field in SENSITIVE_FIELDS:
            if hasattr(record, field):
                setattr(record, field, REDACTED)
        return True
