# HelpDesk Pro

B2B support ticketing and SLA management platform (capstone BC-AINE-007). Customers create
tickets; a rules-based routing engine assigns them to team queues; agents claim, reassign, note
and reply; tickets move through enforced status transitions; an SLA engine tracks timers in
integer minutes and escalates breaches; resolved tickets publish to a knowledge base; admins
manage versioned SLA policies. Synthetic seed data only.

## Prerequisites

- Python 3.11+ and [`uv`](https://docs.astral.sh/uv/)
- Node.js 20+ and npm

## Quick start

```bash
# 1. Install dependencies for both services
./init.sh
# (or manually: cd backend && uv sync && cd ../frontend && npm ci)

# 2. Start the backend (port 8000), in one terminal
cd backend
uv run uvicorn src.main:app --reload --port 8000

# 3. Start the frontend (port 5173), in another terminal
cd frontend
npm run dev -- --port 5173
```

The backend applies its append-only SQL migrations (including seed teams, users and SLA
policies) automatically on startup against a local SQLite database. Check readiness with:

```bash
curl http://localhost:8000/health
```

Then open http://localhost:5173.

## Seed users (synthetic data)

All seeded accounts share the password `Password123!`.

| Username | Role | Team |
|---|---|---|
| `customer1` | customer | — |
| `customer2` | customer | — |
| `admin1` | admin | — |
| `agent1` | agent | Billing |
| `agent2` | agent | Billing |

Seeded teams (queues): Billing, Technical, Account, and their tier-2 escalation queues
(Billing Tier 2, Technical Tier 2, Account Tier 2).

## Tests and linters

**Backend** (from `backend/`):

```bash
uv run pytest -x -q                                   # tests
uv run pytest -q --cov=src --cov-report=term-missing   # tests with coverage
uv run ruff check --fix .                              # lint
uv run mypy src/                                       # strict type check
uv run lint-imports                                    # architecture / layering contract
```

**Frontend** (from `frontend/`):

```bash
npm test         # unit tests
npm run lint      # lint
npm run typecheck # type check
```

**E2E** (from `frontend/`):

```bash
npx playwright test
```

## Architecture

Strict layered architecture: Types/Models → Config → Repository → Service → API → UI.
Business rules live in `backend/src/domain`. One-way dependencies only, enforced by
`import-linter`. See `.claude/architecture.md` for full rules.

## CI

`.gitlab-ci.yml` runs the backend pipeline (lint, type check, architecture check, tests with
coverage) on every push. Frontend and E2E stages are added in a later session.
