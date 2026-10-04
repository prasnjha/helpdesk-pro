"""Start the backend (API on :8000) and the frontend (UI on :5173) with one command.

Usage, from the repo root:
    python scripts/dev.py

Ctrl+C stops both servers. If either server exits on its own, the other is stopped too.
Dependencies must already be installed (./init.sh, or `uv sync` and `npm ci`).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ServiceCommand:
    name: str
    argv: list[str]
    cwd: Path


def service_commands(
    repo_root: Path, which: Callable[[str], str | None] = shutil.which
) -> list[ServiceCommand]:
    """Commands for both servers, with the tool paths resolved up front so a missing
    tool fails before anything starts."""
    uv = _require(which, "uv")
    npm = _require(which, "npm")
    return [
        ServiceCommand(
            name="backend",
            argv=[uv, "run", "uvicorn", "src.main:app", "--reload", "--port", "8000"],
            cwd=repo_root / "backend",
        ),
        ServiceCommand(
            name="frontend",
            argv=[npm, "run", "dev", "--", "--port", "5173"],
            cwd=repo_root / "frontend",
        ),
    ]


def _require(which: Callable[[str], str | None], tool: str) -> str:
    path = which(tool)
    if path is None:
        raise SystemExit(f"'{tool}' was not found on PATH. Install it, then retry.")
    return path


def main() -> int:
    procs: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        for command in service_commands(REPO_ROOT):
            print(f"[dev] starting {command.name}: {' '.join(command.argv)}", flush=True)
            procs.append((command.name, subprocess.Popen(command.argv, cwd=command.cwd)))
        while all(proc.poll() is None for _, proc in procs):
            time.sleep(0.5)
        for name, proc in procs:
            if proc.poll() is not None:
                print(f"[dev] {name} exited with code {proc.returncode}", flush=True)
    except KeyboardInterrupt:
        print("[dev] stopping", flush=True)
    finally:
        for _, proc in procs:
            if proc.poll() is None:
                proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
