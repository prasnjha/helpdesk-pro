"""Layering is enforced by import-linter (backend/CLAUDE.md); run it inside pytest
so a layer violation fails the normal `pytest -x -q` run, not just a separate command.
"""

from __future__ import annotations

import io
import os
from contextlib import redirect_stdout

import importlinter.api  # noqa: F401  (import runs configuration.configure())
from importlinter.application.use_cases import lint_imports

_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_import_linter_contracts_pass() -> None:
    cwd = os.getcwd()
    os.chdir(_BACKEND_ROOT)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            passed = lint_imports(no_logo=True)
    finally:
        os.chdir(cwd)
    assert passed, buffer.getvalue()
