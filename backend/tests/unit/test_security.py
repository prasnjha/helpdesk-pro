from __future__ import annotations

from src.repository.security import hash_password, verify_password


def test_E1S2_verify_password_accepts_correct_password() -> None:
    stored = hash_password("Password123!")
    assert verify_password("Password123!", stored)


def test_E1S2_verify_password_rejects_wrong_password() -> None:
    stored = hash_password("Password123!")
    assert not verify_password("wrong", stored)


def test_E1S2_verify_password_rejects_malformed_stored_value() -> None:
    assert not verify_password("anything", "not-a-valid-hash")
