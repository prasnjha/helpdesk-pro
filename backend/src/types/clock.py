"""Injectable clock. All time reads in domain and service code go through a Clock.

No float arithmetic lives here; this module only produces timestamps.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    """Anything that can report the current UTC time."""

    def now(self) -> datetime:
        """Return the current UTC time."""
        ...


class SystemClock:
    """Real wall-clock time, for production use."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class TestClock:
    """Deterministic clock for tests. Never sleeps; `advance` moves time forward."""

    __test__ = False  # not a pytest test case, despite the name

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start or datetime(2026, 1, 1, tzinfo=UTC)

    def now(self) -> datetime:
        return self._now

    def advance(self, minutes: int) -> None:
        self._now = self._now + timedelta(minutes=minutes)
