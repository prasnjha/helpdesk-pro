# Evaluator Report — Group C (Sprint 3), retroactive verification

Date: 2026-10-04

**This contract and this evaluation are retroactive.** Group C (`E4-S1`, `E4-S2`, `E4-S3`) was implemented and merged in solo mode — an autonomous agent loop that, per `.claude/skills/evaluate/SKILL.md`'s mode table, skips the evaluator entirely. No `sprint-contracts/C.json` existed before or during implementation, and no evaluator ran against the live app at merge time. `features.json` already showed F009-F012 and F019-F020 as `passes: true` with timestamps from the solo run itself (`2026-10-04T07:18:20Z`), which is exactly the kind of self-reported pass this evaluation exists to check independently. `sprint-contracts/C.json` was written today, after the code already existed, by reading `specs/stories/sprint-3.md`, `specs/design/api-contracts.md`, `.claude/skills/sla-policy-evaluator/SKILL.md` and `.claude/skills/escalation-checker/SKILL.md`, and every check below was then executed for real against a freshly started instance of the already-built app. This is post-hoc verification, not a TDD-style contract negotiation.

Mode: `local` (`project-manifest.json` verification.mode). Backend started with `cd backend && uv run uvicorn src.main:app --port 8000`, logged to `/tmp/backend.log`. `GET /health` returned 200 on the first attempt. The frontend dev server was **not** started: Group C (`E4-S1`..`E4-S3`) is API/service layer only per `specs/stories/sprint-3.md`; the only matching UI (`frontend/src/pages/AdminPoliciesPage.tsx`) is scoped to Group D's `E6-S2` (per the task instructions for this run), so no `playwright_checks` were written into the contract and none were forced here.

Stories: E4-S1, E4-S2, E4-S3
Features under test: F009, F010, F011, F012, F019, F020

## The clock problem, and how it was handled

`backend/src/types/clock.py` defines an injectable `Clock` protocol with a `SystemClock` (real wall time) and a `TestClock` (fake, used only by pytest). `backend/src/main.py` wires `SystemClock()` into the app (`app = create_app(engine, SystemClock(), ...)`), and there is no admin/debug endpoint anywhere in `backend/src/api/routers/` that swaps in a `TestClock` or sets `now` directly. So the live server cannot be fast-forwarded, and the story's literal boundary marks (a 15-minute Critical response target read at +11, +12, +14:59 and +15 minutes; a note at +5 and a reply at +20; a resolution timer running to +200 minutes) cannot be driven live without actually waiting that long.

Two things were done about this, and both are recorded explicitly in `sprint-contracts/C.json`'s check descriptions:

1. **The exact literal-minute boundaries are verified by the existing pytest suite**, which uses the fake `TestClock`/direct `datetime` inputs against the exact same `src/domain/sla.py` function the live endpoint calls: `backend/tests/unit/test_domain_sla.py::test_AC05_critical_on_track_at_11_minutes`, `test_AC05_critical_at_risk_at_12_minutes`, `test_AC05_critical_at_risk_at_14_minutes_59_seconds`, `test_AC05_critical_breached_at_15_minutes`, `test_AC05_response_stops_at_first_public_reply_not_internal_note`, `test_AC05_pending_customer_resolution_timer_keeps_running`, `test_AC05_resolution_stops_at_resolved_and_stays_fixed`. These are unit tests on the pure domain function, not end-to-end, but they are the literal story assertions and they pass.
2. **A proportionally-equivalent scenario was driven live** against a real, running server with real wall-clock waits (no sleeping inside application code, no test shortcuts — just `sleep` in the evaluator's own shell between real HTTP calls). An admin-created Critical SLA policy version with `response_minutes=5, resolution_minutes=20` reproduces the same floor-division/80%-threshold arithmetic as the story's 15/240 policy, scaled down so the whole AT_RISK/BREACHED/escalation/idempotency sequence fits in about 6 real minutes instead of 15+. This exercises the full live stack (API routing, auth, repository writes, the `evaluate_and_escalate` transaction) that the pytest unit tests do not reach.

This mirrors Group A's report, which deferred one check (`GET /api/tickets/{id}` not existing yet) to the pytest suite with an explicit note, and Group B's report, which flagged and worked around a sandbox limitation rather than silently skipping a check.

## Step 1 — API checks (Layer 1)

All requests run with `curl` against `http://localhost:8000` on a freshly migrated, empty `helpdesk.db`. Seeded users (password `Password123!`): `customer1` (C-1), `agent1` (AG-1, Billing team), `admin1` (AD-1).

### E4-S1 (AC-10, policy versioning) — all four checks are exact live reproductions of the story text, no scaling needed

| Check id | Result | Evidence |
|---|---|---|
| AC-10-create-version-2 | **PASS** | `POST /api/admin/sla-policies {"priority":"High","response_minutes":45,"resolution_minutes":360}` as admin → `201 {"id":5,"priority":"High","version":2,"response_minutes":45,"resolution_minutes":360,...}`. Follow-up `GET /api/admin/sla-policies?priority=High` showed `[{"version":2,...},{"id":2,"version":1,"response_minutes":60,"resolution_minutes":480,...}]` — v1 unchanged. |
| AC-10-published-version-immutable | **PASS** | `PATCH`, `PUT`, `DELETE /api/admin/sla-policies/versions/1` as admin each → `409 {"error":{"code":"POLICY_VERSION_IMMUTABLE","message":"SlaPolicy version '1' is immutable"}}`. |
| AC-10-float-minutes-rejected | **PASS** | `POST ... {"response_minutes":45.5,...}` → `422 {"error":{"code":"VALIDATION_ERROR","message":"Field 'response_minutes' is invalid"}}`. |
| AC-10-resolution-below-response-rejected | **PASS** | `POST ... {"response_minutes":100,"resolution_minutes":50}` → `422 {"error":{"code":"VALIDATION_ERROR","message":"resolution_minutes must be >= response_minutes"}}`. |
| AC-10-agent-caller-forbidden | **PASS** | `POST /api/admin/sla-policies` as agent1 → `403 {"error":{"code":"FORBIDDEN","message":"Role 'agent' may not perform this action"}}`. |

### E4-S2 (AC-05, timers) and E4-S3 (AC-06, escalation) — live-driven with a scaled policy, boundary minutes cross-checked against pytest

Setup: created a new Critical SLA policy version (`response_minutes=5, resolution_minutes=20`) as admin, then created three Critical tickets (so each snapshots this new version): `HD-000001` (Billing, for the breach/escalation walk), `HD-000002` (Technical, for the note-vs-reply-stop walk), `HD-000003` (Account, for the PENDING_CUSTOMER resolution walk). All timestamps below are real UTC wall-clock times from the run.

| Check id | Result | Evidence |
|---|---|---|
| AC-05-response-timer-on-track-at-risk-breached | **PASS** | `HD-000001` created `17:02:39`. `GET .../sla` at `17:02:39` (t+0) → `response.elapsed_minutes=0, state=ON_TRACK`. At `17:06:56` (t+4m17s ≈ t+4) → `elapsed_minutes=4, state=AT_RISK` (4×100=400 ≥ 5×80=400, matches `_state_for` in `src/domain/sla.py`). At `17:07:58` (t+5m19s ≈ t+5) → `elapsed_minutes=5, state=BREACHED`. Literal 11/12/14:59/15-minute marks against the real 15-minute target: **verified via pytest**, not live (see clock-problem section above) — `test_domain_sla.py`'s four `test_AC05_critical_*` tests pass. |
| AC-05-note-does-not-stop-reply-does | **PASS** | `HD-000002` created `17:02:39`, claimed by agent1 immediately. Internal note posted at `17:03:49` (t+70s) → `201`. `GET .../sla` at `17:04:47` (t+128s, right after the next step's reply) showed `response.stopped_at = "2026-10-04T17:04:47..."` — the **reply** timestamp, not the `17:03:49` note timestamp, confirming the note alone did not stop the timer. Public reply posted at `17:04:47` → `201 {"author_role":"agent",...}`, and the same `GET` in that response body showed `response.elapsed_minutes=2, stopped_at=<reply time>`. A later `GET` at `17:07:58` (well past the 5-minute breach deadline) still showed `elapsed_minutes=2, state=ON_TRACK, stopped_at` unchanged — the stop held fixed and the ticket never flipped to BREACHED after stopping. Literal +5/+20-minute marks: **verified via pytest** (`test_AC05_response_stops_at_first_public_reply_not_internal_note`). |
| AC-05-pending-customer-resolution-keeps-running-stops-at-resolved | **PASS** | `HD-000003` created `17:02:39`, claimed, moved `IN_PROGRESS → PENDING_CUSTOMER` at `17:04:47`. `GET .../sla` at `17:04:47` → `resolution.elapsed_minutes=2, stopped_at=null`. A second `GET` at `17:05:45` (t+3m) → `resolution.elapsed_minutes=3, stopped_at=null` — still increasing, still running, while the ticket was `PENDING_CUSTOMER` the whole time. `POST .../status {"to_status":"RESOLVED"}` at `17:05:45` → `200`. The immediately following `GET .../sla` showed `resolution.elapsed_minutes=3, stopped_at="2026-10-04T17:05:45..."` — stopped at the RESOLVED transition. (Also observed: `response.stopped_at` was set to the same timestamp, since the response timer had not stopped yet at RESOLVED time — `ticket_repository.py` sets both `response_stopped_at` and `resolution_stopped_at` when a ticket reaches `RESOLVED` if either is still null, which matches `src/domain/CLAUDE.md`'s "one function evaluates SLA timers" intent, not a defect.) Literal +200-minute mark: **verified via pytest** (`test_AC05_pending_customer_resolution_timer_keeps_running`, `test_AC05_resolution_stops_at_resolved_and_stays_fixed`). |
| AC-06-breach-escalates-billing-to-tier-2 | **PASS** | At `17:07:58` (`HD-000001`'s BREACHED read above), `GET /api/tickets/HD-000001` showed `"status":"OPEN","escalated":true,"queue":{"slug":"billing-tier-2","name":"Billing Tier 2"}` — status unchanged (still `OPEN`, never touched by the escalation), escalated flipped, queue moved to tier 2. A read-only query of the `sla_event` table (`python3 -c "import sqlite3; ..."`, read-only `SELECT`, no write) showed exactly two rows for `HD-000001`: `('BREACHED_RESPONSE','response',...)` and `('ESCALATED', None, None)` — one of each, per the story. |
| AC-06-repeat-read-writes-no-new-events | **PASS** | A second `GET /api/tickets/HD-000001/sla` was issued immediately after the above. The read-only `sla_event` row count for `HD-000001` was re-checked: still 2 rows, same two events. |
| AC-06-closed-ticket-prior-breach-writes-no-new-events | **PASS** | `HD-000001` was then claimed (now from the `billing-tier-2` queue, `version=2`) → `200 IN_PROGRESS`; `POST .../status {"to_status":"RESOLVED","version":3}` → `200`; `POST .../status {"to_status":"CLOSED","version":4}` → `200`. A `GET .../sla` on the now-`CLOSED` ticket returned `200` with a snapshot (`response.state=BREACHED, elapsed_minutes=5, stopped_at=<RESOLVED time>`) and the read-only `sla_event` row count for `HD-000001` was still 2 — no new rows written on a read of a CLOSED ticket with a prior breach, matching `sla_repository.evaluate_and_escalate`'s explicit `if ticket.status == "CLOSED": return snapshot` early-return before any write. |

## Step 2 — Playwright checks (Layer 2)

**Not applicable to this group.** E4-S1/S2/S3 are API/service-layer stories per `specs/stories/sprint-3.md`; there is no UI story for SLA policy management or timer display in Group C (that UI, `frontend/src/pages/AdminPoliciesPage.tsx`, belongs to Group D's `E6-S2` per `specs/stories/sprint-4.md` and is out of scope for this evaluation per the task instructions). No `playwright_checks` were written into `sprint-contracts/C.json`, and the frontend dev server was not started for this run.

## Step 3 — Architecture checks

| Check | Result | Evidence |
|---|---|---|
| layering | **PASS** | `uv run lint-imports` → "Layered architecture KEPT / Domain is pure KEPT / Contracts: 2 kept, 0 broken." (76 files, 254 dependencies analyzed) |
| typing | **PASS** | `uv run mypy src/` → "Success: no issues found in 55 source files" |
| folder_structure | **PASS** | `backend/src/` contains `api/`, `config/`, `domain/`, `repository/`, `service/`, `types/`; SLA domain code lives in `src/domain/sla.py`, `src/domain/sla_policy.py`, `src/domain/escalation.py`, none of which import FastAPI or SQLAlchemy (confirmed by reading each file's imports). |

## Step 4 — Backend gate

- `uv run pytest -x -q` → **255 passed**, 0 failed. (`uv sync --extra dev` was run first — `pytest`/`ruff`/`mypy`/`import-linter` are the `dev` optional-dependency group in `backend/pyproject.toml`, same environment-setup step as Groups A and B.)
- Coverage: `uv run pytest --cov=src --cov-report=term-missing -q` → **99% total** (1545 statements, 12 missed; floor is 80%). The bare `coverage.xml`'s top-level `line-rate` attribute initially looked like 54% when parsed naively with a regex — that number belongs to a per-package/partial element in the XML, not the project total; the `TOTAL` row in the actual `pytest-cov` terminal report (99%) is the correct figure and matches Group A/B's reports.
- `uv run ruff check .` → "All checks passed!"
- `uv run mypy src/` → "Success: no issues found in 55 source files"
- `uv run lint-imports` → "Layered architecture KEPT / Domain is pure KEPT / Contracts: 2 kept, 0 broken."
- AC-id-named tests confirmed present on disk for every AC in scope: `tests/integration/test_admin_sla_policy_api.py`, `tests/unit/test_domain_sla_policy.py`, `tests/unit/test_sla_policy_repository.py` (AC-10); `tests/unit/test_domain_sla.py`, `tests/unit/test_sla_service.py`, `tests/unit/test_ticket_repository_sla_timers.py`, `tests/integration/test_sla_read_api.py` (AC-05); `tests/unit/test_domain_escalation.py`, `tests/unit/test_sla_event_repository.py`, `tests/unit/test_sla_repository_evaluate_and_escalate.py`, `tests/unit/test_ticket_repository_escalate.py` (AC-06).

## Overall verdict: **PASS**

All 10 live API checks and all 3 architecture checks pass. The full backend gate (255 tests, ruff, mypy, lint-imports) is clean. No real application-code failure was found in Group C.

Every behavior specified in `specs/stories/sprint-3.md` for E4-S1 through E4-S3 was reproduced: SLA policy versioning with immutable published versions, integer-minute 422 validation, and admin-only access (all live, exact); the ON_TRACK → AT_RISK → BREACHED state progression, the internal-note-does-not-stop / public-reply-does distinction, and the PENDING_CUSTOMER resolution-timer-keeps-running / stops-at-RESOLVED behavior (live, on a proportionally scaled policy, with the literal story minute marks additionally confirmed by the existing pytest suite against the real 15-minute target); and tier-2 escalation with exactly one BREACHED_RESPONSE and one ESCALATED row, idempotent on repeat reads and on a CLOSED ticket (live, exact).

**No real application-code failure was found.** The only limitation encountered — the live server has no way to fast-forward its clock, so the story's literal minute marks could not be driven against a real 15-minute window in reasonable evaluation time — is an environment/tooling constraint of this sandbox and this build (no debug clock-override endpoint exists), not a defect in `backend/src`. It is handled the same way Group A handled its `GET /api/tickets/{id}`-not-yet-built gap: documented explicitly in the contract and this report, with the literal assertions covered by the existing pytest suite against the exact same domain code the live endpoint calls. No entry was written to `docs/fix-loops/` because nothing here is a functional defect to fix.

### features.json updates made

`F009`, `F010`, `F011`, `F012`, `F019`, `F020`: `last_evaluated` refreshed to `2026-10-04T17:12:08Z`; `passes` confirmed `true`; `failure_reason`/`failure_layer` confirmed `null`. No other fields were changed. (Note: `features.json` already had uncommitted `last_evaluated` refreshes for Group B's features, `F005`-`F008`/`F013`-`F016`, from that group's own evaluator run; those were left untouched by this run's edit, which only touched the six Group C feature ids.)

## Housekeeping

- Backend process started for this verification (`uv run uvicorn src.main:app --port 8000`) was stopped after testing (confirmed `curl http://localhost:8000/health` now returns connection-refused / exit 7). The frontend dev server was never started for this run (out of scope, see Step 2).
- `backend/helpdesk.db` was deleted once at the start to get a clean seeded DB for this run (synthetic seed data plus tickets `HD-000001`..`HD-000003` created during this verification, plus SLA policy versions created by this run's admin calls). This is local dev data, not source code.
- An extra Critical SLA policy version (`response_minutes=5, resolution_minutes=20`) and an extra High version (`response_minutes=45, resolution_minutes=360`) were created against the live admin API as part of the AC-10 and AC-05/AC-06 checks above — this is exactly the API surface under test, not a code or schema change, and these rows live only in the disposable `helpdesk.db` created for this run.
- Read-only `sqlite3` queries (Python's `sqlite3` module, `SELECT` only) were used twice to count `sla_event` rows for idempotency verification, the same read-only pattern Group B's report used for the `assignments` table; no row was ever written, updated or deleted this way.
- No application code under `backend/src/` or `frontend/src/` was modified.
