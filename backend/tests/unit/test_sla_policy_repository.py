"""AC-10: SLA policy versioning repository (admin-console_spec.md).
Append-only: insert and read only, no update or delete.
"""

from __future__ import annotations

import inspect

from src.repository import sla_policy_repository
from src.types.clock import TestClock

_FORBIDDEN_NAME_FRAGMENTS = ("update", "delete", "remove", "edit", "modify")


def test_AC10_sla_policy_repository_has_no_update_or_delete_method() -> None:
    functions = inspect.getmembers(sla_policy_repository, inspect.isfunction)
    names = [name for name, _ in functions if not name.startswith("_")]
    assert names
    for name in names:
        lowered = name.lower()
        assert not any(fragment in lowered for fragment in _FORBIDDEN_NAME_FRAGMENTS)


def test_AC10_insert_version_creates_version_2_and_leaves_version_1_unchanged(engine) -> None:
    clock = TestClock()
    with engine.begin() as conn:
        v1_id = sla_policy_repository.get_active_version_id(conn, "High")
        record = sla_policy_repository.insert_version(
            conn,
            priority="High",
            response_minutes=45,
            resolution_minutes=360,
            created_by="AD-1",
            published_at=clock.now().isoformat(),
        )
    assert record.version == 2
    assert record.priority == "High"
    assert record.response_minutes == 45
    assert record.resolution_minutes == 360
    with engine.connect() as conn:
        v1 = sla_policy_repository.get_by_id(conn, v1_id)
    assert v1 is not None
    assert v1.response_minutes == 60
    assert v1.resolution_minutes == 480


def test_AC10_get_by_id_returns_none_for_unknown_id(engine) -> None:
    with engine.connect() as conn:
        assert sla_policy_repository.get_by_id(conn, 999_999) is None


def test_AC10_list_versions_newest_first(engine) -> None:
    clock = TestClock()
    with engine.begin() as conn:
        sla_policy_repository.insert_version(
            conn,
            priority="High",
            response_minutes=45,
            resolution_minutes=360,
            created_by="AD-1",
            published_at=clock.now().isoformat(),
        )
    with engine.connect() as conn:
        versions = sla_policy_repository.list_versions(conn, priority="High")
    assert [v.version for v in versions] == [2, 1]


def test_AC10_list_versions_without_priority_returns_all(engine) -> None:
    with engine.connect() as conn:
        versions = sla_policy_repository.list_versions(conn, priority=None)
    assert len(versions) == 4


def test_AC10_get_targets_returns_response_and_resolution_minutes(engine) -> None:
    with engine.connect() as conn:
        policy_id = sla_policy_repository.get_active_version_id(conn, "Critical")
        assert policy_id is not None
        targets = sla_policy_repository.get_targets(conn, policy_id)
    assert targets == (15, 240)
