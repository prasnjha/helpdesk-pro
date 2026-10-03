"""Password hashing for seeded users. Synthetic data only (project constraint)."""

from __future__ import annotations

import hashlib
import hmac
import os

_ITERATIONS = 100_000


def hash_password(password: str, salt: str | None = None) -> str:
    """Return `salt$hash` using PBKDF2-HMAC-SHA256."""
    salt = salt or os.urandom(16).hex()
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), _ITERATIONS)
    return f"{salt}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    candidate = hash_password(password, salt=salt)
    return hmac.compare_digest(candidate, stored)
