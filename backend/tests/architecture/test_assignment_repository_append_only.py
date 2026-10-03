"""Structural check for agent-workbench_spec.md AC-03: "Given the Assignment
repository, When code is inspected or the architecture test runs, Then no update
or delete method exists for Assignment rows."
"""

from __future__ import annotations

import inspect

from src.repository import assignment_repository

_FORBIDDEN_NAME_FRAGMENTS = ("update", "delete", "remove", "edit", "modify")


def test_AC03_assignment_repository_has_no_update_or_delete_method() -> None:
    functions = inspect.getmembers(assignment_repository, inspect.isfunction)
    names = [name for name, _ in functions if not name.startswith("_")]

    assert names, "expected assignment_repository to expose at least one function"
    for name in names:
        lowered = name.lower()
        assert not any(fragment in lowered for fragment in _FORBIDDEN_NAME_FRAGMENTS), (
            f"assignment_repository.{name} looks like an update/delete method; "
            "Assignment rows must stay append-only (insert and read only)"
        )
