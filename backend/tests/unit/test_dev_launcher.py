"""Unit tests for scripts/dev.py, the single command that starts the backend (API :8000)
and the frontend (UI :5173). Only the pure command-building function is tested; the
process supervision in main() is exercised by running `python scripts/dev.py`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_dev_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("dev_launcher", _REPO_ROOT / "scripts" / "dev.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses looks the module up by name
    spec.loader.exec_module(module)
    return module


def _fake_which(name: str) -> str | None:
    return {"uv": "/bin/uv", "npm": "/bin/npm"}.get(name)


def test_service_commands_start_backend_on_8000_and_frontend_on_5173() -> None:
    dev = _load_dev_module()

    commands = {c.name: c for c in dev.service_commands(_REPO_ROOT, which=_fake_which)}

    assert set(commands) == {"backend", "frontend"}
    assert commands["backend"].argv == [
        "/bin/uv",
        "run",
        "uvicorn",
        "src.main:app",
        "--reload",
        "--port",
        "8000",
    ]
    assert commands["backend"].cwd == _REPO_ROOT / "backend"
    assert commands["frontend"].argv == ["/bin/npm", "run", "dev", "--", "--port", "5173"]
    assert commands["frontend"].cwd == _REPO_ROOT / "frontend"


def test_service_commands_fail_with_a_clear_message_when_a_tool_is_missing() -> None:
    dev = _load_dev_module()

    def no_npm(name: str) -> str | None:
        return "/bin/uv" if name == "uv" else None

    with pytest.raises(SystemExit, match="npm"):
        dev.service_commands(_REPO_ROOT, which=no_npm)
