"""NFR-03: known names come from the users table and refresh after a user row changes."""

from __future__ import annotations

from sqlalchemy import Engine, text

from src.config.log_redaction import expand_name_variants, redact_text
from src.repository import user_repository
from src.service.known_names_service import refresh_known_names


def test_NFR03_display_name_expands_to_full_first_and_last_name() -> None:
    assert expand_name_variants("Priya Raman") == {"Priya Raman", "Priya", "Raman"}


def test_NFR03_single_word_display_name_is_its_own_only_variant() -> None:
    assert expand_name_variants("Cher") == {"Cher"}


def test_NFR03_seeded_users_carry_synthetic_display_names(engine: Engine) -> None:
    with engine.connect() as conn:
        names = user_repository.list_display_names(conn)

    assert "Priya Raman" in names
    assert "Dana Whitfield" in names
    assert len(names) == 5


def test_NFR03_known_names_refresh_when_a_user_row_is_added(engine: Engine) -> None:
    refresh_known_names(engine)
    assert redact_text("Sofia Lind asked about billing") == "Sofia Lind asked about billing"

    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (id, username, password_hash, role, team_id, active, "
                "display_name) VALUES ('C-9', 'customer9', 'x', 'customer', NULL, 1, "
                "'Sofia Lind')"
            )
        )
    refresh_known_names(engine)

    assert redact_text("Sofia Lind asked about billing") == (
        "[REDACTED_NAME] asked about billing"
    )
