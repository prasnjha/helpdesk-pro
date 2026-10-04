"""PII redaction for log output (NFR-03).

Masks, in order: email addresses, phone numbers, known personal names (from the users
table, see `KnownNames`), then names that follow a greeting or sign-off, or "my name
is" / "I am". Ticket subject, title, body and description fields on a record are
masked outright. Stdlib only, so the config layer stays free of upward imports.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable

REDACTED = "[REDACTED]"
REDACTED_EMAIL = "[REDACTED_EMAIL]"
REDACTED_PHONE = "[REDACTED_PHONE]"
REDACTED_NAME = "[REDACTED_NAME]"

SENSITIVE_FIELDS = frozenset(
    {
        "body",
        "description",
        "subject",
        "title",
        "ticket_body",
        "ticket_description",
        "ticket_subject",
        "ticket_title",
    }
)

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Candidate phone: optional +, then digits with common separators. The digit count
# is checked separately so short numbers and dates are left alone.
_PHONE_CANDIDATE = re.compile(r"(?<![\w+])\(?\+?\d(?:[\s().-]{0,2}\d){8,14}(?!\w)")
_MIN_PHONE_DIGITS = 10
_MAX_PHONE_DIGITS = 15

_MIN_KNOWN_NAME_CHARS = 2
_NAME_WORD = r"[A-Z][A-Za-z'\-]+"
_NAME_PHRASE = rf"{_NAME_WORD}(?:\s+{_NAME_WORD}){{0,2}}"
_GREETING = re.compile(
    rf"(?P<lead>\b(?i:hi|hello|hey|dear|regards|thanks|thank you|cheers|sincerely)\b[,!]?\s+)"
    rf"(?P<name>{_NAME_PHRASE})"
)
_INTRO = re.compile(rf"(?P<lead>\b(?i:my name is|i am)\s+)(?P<name>{_NAME_PHRASE})")

# Capitalised words that are common in greetings, sign-offs and ordinary sentences.
# A name phrase is cut at the first of these, so "Hi Jordan Blake Support" keeps
# "Jordan Blake" and "Hi Team" or "I am Sorry" masks nothing.
NAME_STOP_WORDS = frozenset(
    {
        "again", "admin", "agent", "all", "also", "back", "both", "customer", "dear",
        "desk", "everybody", "everyone", "fine", "folks", "friend", "friends", "glad",
        "good", "great", "guys", "happy", "helpdesk", "hello", "here", "hi", "madam",
        "not", "ops", "please", "regards", "sir", "sorry", "sure", "support", "team",
        "thank", "thanks", "there", "ticket", "unable", "very", "world", "you",
    }
)  # fmt: skip


def expand_name_variants(display_name: str) -> set[str]:
    """Full name, first name and last name of one display name."""
    cleaned = " ".join(display_name.split())
    if not cleaned:
        return set()
    parts = cleaned.split(" ")
    return {cleaned, parts[0], parts[-1]}


class KnownNames:
    """Names from the users table, matched case-insensitively on word boundaries."""

    def __init__(self) -> None:
        self._pattern: re.Pattern[str] | None = None

    def replace(self, display_names: Iterable[str]) -> None:
        variants: set[str] = set()
        for display_name in display_names:
            variants |= expand_name_variants(display_name)
        usable = sorted(
            (v for v in variants if len(v) >= _MIN_KNOWN_NAME_CHARS),
            key=len,
            reverse=True,
        )
        if not usable:
            self._pattern = None
            return
        alternatives = "|".join(re.escape(name) for name in usable)
        self._pattern = re.compile(rf"\b(?:{alternatives})\b", re.IGNORECASE)

    def mask(self, text: str) -> str:
        if self._pattern is None:
            return text
        return self._pattern.sub(REDACTED_NAME, text)


known_names = KnownNames()


def _mask_phone(match: re.Match[str]) -> str:
    digits = sum(ch.isdigit() for ch in match.group(0))
    if _MIN_PHONE_DIGITS <= digits <= _MAX_PHONE_DIGITS:
        return REDACTED_PHONE
    return match.group(0)


def _mask_name_phrase(match: re.Match[str]) -> str:
    name = match.group("name")
    cut = len(name)
    for token in re.finditer(r"\S+", name):
        if token.group().lower() in NAME_STOP_WORDS:
            cut = token.start()
            break
    kept = name[:cut].rstrip()
    if not kept:
        return match.group(0)
    return match.group("lead") + REDACTED_NAME + name[len(kept) :]


def redact_text(text: str, names: KnownNames | None = None) -> str:
    registry = known_names if names is None else names
    masked = _EMAIL.sub(REDACTED_EMAIL, text)
    masked = _PHONE_CANDIDATE.sub(_mask_phone, masked)
    masked = registry.mask(masked)
    masked = _GREETING.sub(_mask_name_phrase, masked)
    return _INTRO.sub(_mask_name_phrase, masked)


class RedactionFilter(logging.Filter):
    """Masks PII in the formatted message, sensitive record attributes and structured fields."""

    def __init__(self, names: KnownNames | None = None) -> None:
        super().__init__()
        self._names = names

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage(), self._names)
        record.args = ()
        for field in SENSITIVE_FIELDS:
            if hasattr(record, field):
                setattr(record, field, REDACTED)
        fields = getattr(record, "json_fields", None)
        if isinstance(fields, dict):
            record.json_fields = {
                key: redact_text(value, self._names) if isinstance(value, str) else value
                for key, value in fields.items()
            }
        return True
