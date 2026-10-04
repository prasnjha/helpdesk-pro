"""NFR-03: personal names are masked as [REDACTED_NAME].

Three deterministic rules: (a) known names from the users table, (b) greeting and
sign-off patterns, (c) "my name is X" and "I am X". Every value is synthetic.
"""

from __future__ import annotations

import pytest

from src.config.log_redaction import KnownNames, redact_text


def _known(*display_names: str) -> KnownNames:
    names = KnownNames()
    names.replace(list(display_names))
    return names


def test_NFR03_known_full_name_is_masked_case_insensitively() -> None:
    names = _known("Priya Raman")

    assert redact_text("Ticket from priya raman today", names) == (
        "Ticket from [REDACTED_NAME] today"
    )


def test_NFR03_known_first_name_is_masked() -> None:
    names = _known("Priya Raman")

    assert redact_text("Priya says hello", names) == "[REDACTED_NAME] says hello"


def test_NFR03_known_last_name_is_masked() -> None:
    names = _known("Priya Raman")

    assert redact_text("Escalated for Raman", names) == "Escalated for [REDACTED_NAME]"


def test_NFR03_known_names_match_whole_words_only() -> None:
    names = _known("Priya Raman")

    assert redact_text("Ramanujan wrote Priyanka", names) == "Ramanujan wrote Priyanka"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hi Jordan Blake,", "Hi [REDACTED_NAME],"),
        ("Hello Jordan,", "Hello [REDACTED_NAME],"),
        ("Dear Jordan Blake,", "Dear [REDACTED_NAME],"),
        ("Thanks, Jordan Blake", "Thanks, [REDACTED_NAME]"),
        ("Thank you, Jordan", "Thank you, [REDACTED_NAME]"),
        ("Regards,\nJordan Blake", "Regards,\n[REDACTED_NAME]"),
    ],
)
def test_NFR03_greeting_and_sign_off_patterns_mask_the_name(text: str, expected: str) -> None:
    assert redact_text(text, KnownNames()) == expected


def test_NFR03_my_name_is_pattern_masks_the_name() -> None:
    assert redact_text("my name is Jordan Blake.", KnownNames()) == (
        "my name is [REDACTED_NAME]."
    )


def test_NFR03_i_am_pattern_masks_the_name() -> None:
    assert redact_text("I am Jordan Blake and I need help", KnownNames()) == (
        "I am [REDACTED_NAME] and I need help"
    )


def test_NFR03_a_stop_word_ends_a_name_phrase() -> None:
    assert redact_text("Hi Jordan Blake Support", KnownNames()) == (
        "Hi [REDACTED_NAME] Support"
    )


@pytest.mark.parametrize(
    "text",
    [
        "Thanks for the quick reply.",
        "Hi Team, the printer is down.",
        "Hello World from the helpdesk",
        "Regards, Support",
        "Dear Customer, your ticket is closed.",
        "Thank you, Agent",
        "Hi there, please advise.",
        "I am Sorry for the delay.",
        "I am Happy with the fix.",
        "I am unable to log in.",
        "my name is missing from the form.",
        "Will the invoice be refunded?",
    ],
)
def test_NFR03_ordinary_words_are_not_masked_as_names(text: str) -> None:
    assert redact_text(text, KnownNames()) == text


def test_NFR03_a_common_word_is_not_masked_unless_it_is_a_known_name() -> None:
    assert redact_text("Will the refund arrive?", _known("Priya Raman")) == (
        "Will the refund arrive?"
    )


def test_NFR03_known_names_are_applied_before_the_pattern_rules() -> None:
    names = _known("Priya Raman")

    assert redact_text("Hi Priya Raman, thanks", names) == "Hi [REDACTED_NAME], thanks"
