# Backend

FastAPI on Python 3.12, SQLAlchemy 2.x, SQLite. Entry point `src/main.py`, run with `uv run uvicorn src.main:app --port 8000`.

## Layers (one-way, enforced by import-linter)

`types` then `config` then `repository` then `service` then `api`. Business rules live in `src/domain` and import nothing from FastAPI or SQLAlchemy.

## Commands

`uv run pytest -x -q`, `uv run ruff check --fix .`, `uv run mypy src/`, `uv run lint-imports`.

## Rules

- Spec wins over code: `specs/` and `specs/design/api-contracts.md`.
- Time comes from the injected Clock. Never call `datetime.now()` in domain or service code.
- Append-only tables are insert-only: history, assignments, notes, replies, SLA events, SLA policy versions, notifications.
- Every AC needs a test whose name contains its id.