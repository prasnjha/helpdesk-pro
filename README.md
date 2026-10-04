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

# 2. Start the backend (API on :8000) and the frontend (UI on :5173) together
python scripts/dev.py
```

`scripts/dev.py` runs both servers and stops both on Ctrl+C. To start them in separate terminals
instead: `cd backend && uv run uvicorn src.main:app --reload --port 8000` and
`cd frontend && npm run dev -- --port 5173`.

The backend applies its append-only SQL migrations (including seed teams, users and SLA
policies) automatically on startup against a local SQLite database. Check readiness with:

```bash
curl http://localhost:8000/health
```

Then open http://localhost:5173.

### Configuration

| Env var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | local SQLite file under `backend/` | Backend database connection |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of origins the API accepts browser requests from (no wildcard) |
| `LOG_LEVEL` | `INFO` | Log level for the JSON log lines (DEBUG, INFO, WARNING, ERROR) |

### Optional: demo tickets

The quick start above gives you an empty, working app. To also see the full lifecycle —
queues, SLA breaches, a knowledge base article, every status — seed about 15 demo tickets
(titled `[DEMO] ...`) through the real API logic:

```bash
cd backend
uv run python scripts/seed_demo_tickets.py
```

It is safe to re-run: it skips seeding if demo tickets already exist. One Billing ticket is
seeded already escalated to the Billing Tier 2 queue after a response breach.

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
uv run pytest -x -q                                   # tests (also writes coverage.xml)
uv run pytest --cov-report=term-missing --cov-fail-under=80   # coverage report, enforce 80% floor
uv run ruff check --fix .                              # lint
uv run mypy src/                                       # strict type check
uv run lint-imports                                    # architecture / layering contract
```

`backend/coverage.xml` is committed as a snapshot of the last test run. Pytest regenerates it, and CI uploads it as a build artifact.

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

## Pages

| Path | Role | Purpose |
|---|---|---|
| `/login` | any | Sign in |
| `/tickets` | customer | Own ticket list, link to a new ticket |
| `/tickets/new` | customer | Create a ticket |
| `/tickets/:id` | customer | Ticket detail, SLA state, reply box |
| `/agent/queues/:queue` | agent, admin | Queue with priority/status/escalated filters |
| `/agent/tickets/:id` | agent, admin | Ticket detail, SLA state, claim, reassign, status, notes, history and a publish-to-KB link |
| `/admin/sla-policies` | admin | SLA policy editor with version history |
| `/admin/dashboard` | admin | Dashboard tables |
| `/kb` | any | Knowledge base search and list |
| `/kb/:id` | any | Article detail (editor controls for agent/admin only) |
| `/agent/kb/new`, `/agent/kb/:id/edit` | agent, admin | Publish or edit form |

## CI

`.gitlab-ci.yml` runs lint, type check, architecture check, and tests for both backend and
frontend, plus a Playwright E2E stage across 375/768/1280 px viewports, on every push. Backend
tests report coverage (`backend/coverage.xml`, floor 80%), kept as a build artifact. Frontend
unit tests produce no coverage report. `.github/workflows/ci.yml` runs the same checks on GitHub.

Both pipelines have an optional Claude Code review of the diff. It runs only when an API key is
set: the `ANTHROPIC_API_KEY` repository secret on GitHub (pull requests, via
`anthropics/claude-code-action`), or the `ANTHROPIC_API_KEY` CI/CD variable on GitLab (merge
request pipelines, via `claude -p`, `allow_failure: true`). Without the key the job is skipped
and the pipeline stays green.
