"""Structural check: modules under src/domain must not import from src.api or
src.repository. Business rules stay pure; the layers above and below them depend
on the domain, never the reverse (.claude/architecture.md).

This is an AST scan inside pytest, so a violation fails the normal test run. It
complements the import-linter "Domain is pure" contract in pyproject.toml.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
_DOMAIN_ROOT = _SRC_ROOT / "domain"
_FORBIDDEN_PREFIXES = ("src.api", "src.repository")


def _imported_modules(source: str, package: str) -> list[str]:
    """Absolute names of every module the source imports. Relative imports are
    resolved against `package`, the package that contains the source file."""
    names: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                names.append(node.module or "")
                continue
            parts = package.split(".")
            anchor = parts[: len(parts) - (node.level - 1)]
            names.append(".".join([*anchor, node.module] if node.module else anchor))
    return names


def find_boundary_violations(source: str, package: str) -> list[str]:
    """Imported module names that fall under a forbidden prefix."""
    return [
        name
        for name in _imported_modules(source, package)
        if any(name == p or name.startswith(p + ".") for p in _FORBIDDEN_PREFIXES)
    ]


def test_detector_flags_absolute_import_from_api() -> None:
    source = "from src.api.routers import tickets\n"
    assert find_boundary_violations(source, "src.domain") == ["src.api.routers"]


def test_detector_flags_plain_import_of_repository_module() -> None:
    source = "import src.repository.ticket_repository\n"
    assert find_boundary_violations(source, "src.domain") == ["src.repository.ticket_repository"]


def test_detector_flags_relative_import_that_climbs_into_repository() -> None:
    source = "from ..repository import ticket_repository\n"
    assert find_boundary_violations(source, "src.domain") == ["src.repository"]


def test_detector_allows_types_config_and_stdlib_imports() -> None:
    source = (
        "from src.types.errors import ValidationError\n"
        "from datetime import datetime, timedelta\n"
        "from . import sla\n"
    )
    assert find_boundary_violations(source, "src.domain") == []


def test_domain_modules_do_not_import_api_or_repository() -> None:
    domain_files = sorted(_DOMAIN_ROOT.glob("*.py"))
    assert domain_files, f"expected domain modules under {_DOMAIN_ROOT}"

    violations: list[str] = []
    for path in domain_files:
        relative = path.relative_to(_SRC_ROOT.parent)
        package = ".".join(path.relative_to(_SRC_ROOT.parent).parent.parts)
        for name in find_boundary_violations(path.read_text(encoding="utf-8"), package):
            violations.append(f"{relative.as_posix()} imports {name}")

    assert violations == [], "domain must not import api or repository:\n" + "\n".join(violations)
