# Evaluator Report — Group B (Sprint 2), retroactive verification

Date: 2026-10-04

**This contract and this evaluation are retroactive.** Group B (`E3-S1`..`E3-S4`) was implemented and merged in solo mode — an autonomous agent loop that, per `.claude/skills/evaluate/SKILL.md`'s mode table, skips the evaluator entirely ("Solo mode: skipping evaluator and exit"). No `sprint-contracts/B.json` existed before or during implementation, and no evaluator ran against the live app at merge time. `sprint-contracts/B.json` was written today, after the code already existed, by reading `specs/stories/sprint-2.md`, `specs/ticket-lifecycle_spec.md`, and `specs/design/api-contracts.md`, and every check below was then executed for real against a freshly started instance of the already-built app. This is a post-hoc verification, not a TDD-style contract negotiation — the contract did not shape the implementation, and a FAIL here would not have been caught before merge the way it would in a Lean/Full run.

Mode: `local` (`project-manifest.json` verification.mode). Backend started with `cd backend && uv run uvicorn src.main:app --port 8000`, frontend with `cd frontend && npm run dev -- --port 5173`, both logged to `/tmp/backend.log` / `/tmp/frontend.log` for this run. `GET /health` returned 200 on the first attempt.

Stories: E3-S1, E3-S2, E3-S3, E3-S4
Features under test: F005, F006, F007, F008, F013, F014, F015, F016

Seeded users used (from `backend/src/repository/migrations/001_core.sql` and `005_workbench.sql`, password `Password123!` for all): `customer1` (C-1), `customer2` (C-2), `agent1` (AG-1, Billing team), `agent2` (AG-2, Billing team), `admin1` (AD-1). All five logins were exercised live and returned 200 with a bearer token.

## Step 1 — API checks (Layer 1)

All requests run with `curl` against `http://localhost:8000` on a freshly migrated, empty `helpdesk.db` (deleted and recreated by the migration runner at backend startup). Ticket ids below are sequential because the DB started empty for this run.

| Check id | Result | Evidence |
|---|---|---|
| AC-04-six-valid-edges | **PASS** | Walked `HD-000001` through `OPEN->IN_PROGRESS` (v1, `200 {"status":"IN_PROGRESS"}`), `IN_PROGRESS->PENDING_CUSTOMER` (v2, `200`), `PENDING_CUSTOMER->RESOLVED` (v3, `200`), `RESOLVED->CLOSED` (v4, `200`). `GET /api/tickets/HD-000001` afterward showed exactly 4 `STATUS_CHANGED` history rows (plus the 1 `ROUTED` row from creation) each with the correct from/to/actor. Walked a second ticket (`HD-000002`) through claim (`OPEN->IN_PROGRESS`) then `IN_PROGRESS->RESOLVED` as agent2 (v3, `200 {"status":"RESOLVED"}`), and a third ticket (`HD-000003`) through `PENDING_CUSTOMER->OPEN` via a customer reply (see AC-08 checks). All six edges from `ticket-lifecycle_spec.md` Section 2 confirmed live, one history row each. |
| AC-04-invalid-transition | **PASS** | `POST /api/tickets/HD-000001/status {"to_status":"RESOLVED","version":1}` while `HD-000001` was still `OPEN` → `409 {"error":{"code":"INVALID_TICKET_STATE","message":"Cannot transition from 'OPEN' to 'RESOLVED'"}}`. Follow-up `GET` confirmed status was still `OPEN` and history still had only the 1 `ROUTED` row. |
| AC-04-closed-ticket-immutable | **PASS** | On `HD-000001` after it reached `CLOSED`: `POST .../status {"to_status":"OPEN","version":5}` → `409 INVALID_TICKET_STATE` (status-endpoint path, matches `ticket-lifecycle_spec.md` AC-04's explicit distinction); `POST .../claim` → `409 {"error":{"code":"TICKET_CLOSED_IMMUTABLE",...}}`; `POST .../notes` → `409 TICKET_CLOSED_IMMUTABLE`; `POST .../replies` → `409 TICKET_CLOSED_IMMUTABLE`. All four live. |
| AC-03-claim-open-ticket | **PASS** | `POST /api/tickets/HD-000002/claim {"version":1}` → `200 {"id":"HD-000002","status":"IN_PROGRESS","assignee_id":"AG-1"}`. Direct read of the `assignments` table (read-only `sqlite3` query, no write) showed row `(1, 'HD-000002', from_user_id=NULL, to_user_id='AG-1', actor_id='AG-1', ...)`. |
| AC-03-reassign-ticket | **PASS** | `POST /api/tickets/HD-000002/reassign {"assignee_id":"AG-2","version":2}` → `200 {"status":"IN_PROGRESS","assignee_id":"AG-2"}` — status unchanged. `assignments` table showed a second row `(2, 'HD-000002', from_user_id='AG-1', to_user_id='AG-2', actor_id='AG-1', ...)`. |
| AC-03-stale-version-conflict | **PASS** | `POST /api/tickets/HD-000002/claim {"version":99}` → `409 {"error":{"code":"VERSION_CONFLICT","message":"Ticket 'HD-000002' was updated by someone else"}}`. |
| AC-07-agent-note-hidden-from-customer | **PASS** | As agent1 (assigned via claim) on `HD-000003`: `POST .../notes {"body":"INTERNAL-NOTE-SECRET checked logs"}` → `201 {"id":1,"ticket_id":"HD-000003","author_id":"AG-1","body":"INTERNAL-NOTE-SECRET checked logs",...}`. `GET /api/tickets/HD-000003` with customer1's token returned `"notes":[]` (and `"history":[]`) — the note body appears nowhere in the customer's response. `GET /api/tickets` (list) as customer1 also carries no note content (list rows only have id/title/status/priority/category/updated_at). |
| AC-07-agent-public-reply-visible | **PASS** | `POST /api/tickets/HD-000003/replies {"body":"PUBLIC-REPLY visible to customer"}` as agent1 → `201 {"author_role":"agent",...}`. `GET /api/tickets/HD-000003` as customer1 showed this reply in `"replies":[...]`. |
| AC-07-notes-replies-immutable | **PASS** | `PUT`, `PATCH`, `DELETE` on `/api/tickets/HD-000003/notes/1` each → `405 {"error":{"code":"METHOD_NOT_ALLOWED","message":"Notes are append-only; no update or delete method exists"}}`. Same three methods on `/api/tickets/HD-000003/replies/1` each → `405 {"error":{"code":"METHOD_NOT_ALLOWED","message":"Replies are append-only; no update or delete method exists"}}`. A follow-up `GET` showed the note and reply rows unchanged (same id, body, created_at). |
| AC-08-reply-pending-customer-moves-to-open | **PASS** | `HD-000003` moved `IN_PROGRESS->PENDING_CUSTOMER` by agent1, then `POST /api/tickets/HD-000003/replies {"body":"Attached the invoice"}` as customer1 → `201 {"author_role":"customer",...,"status":"OPEN"}`. `GET` detail confirmed status `OPEN` and exactly one new history row `{"event":"STATUS_CHANGED","from_state":"PENDING_CUSTOMER","to_state":"OPEN","actor_id":"C-1"}`. |
| AC-08-reply-open-status-unchanged | **PASS** | A second reply on the now-`OPEN` `HD-000003` as customer1 → `201 {...,"status":"OPEN"}` — status unchanged, no new status-change history row. |
| AC-08-reply-resolved-rejected | **PASS** | `HD-000002` was `RESOLVED` (from the AC-04 edge walk). `POST /api/tickets/HD-000002/replies {"body":"trying to reply on resolved"}` as customer1 (owner) → `409 {"error":{"code":"INVALID_TICKET_STATE","message":"Cannot reply to a ticket in 'RESOLVED'"}}`. Follow-up `GET` confirmed `"replies":[]` on `HD-000002` — no row written. |
| AC-08-reply-other-customers-ticket-404 | **PASS** | `POST /api/tickets/HD-000003/replies` (owned by customer1/C-1) with customer2's token → `404 {"error":{"code":"NOT_FOUND","message":"Ticket 'HD-000003' not found"}}`. |
| (extra, not in sprint-2 ACs but in api-contracts.md role rules) customer calling status/claim/notes | **PASS** | As customer1: `POST .../status` → `403 FORBIDDEN`; `POST .../claim` → `403 FORBIDDEN`; `POST .../notes` → `403 FORBIDDEN`. |

## Step 2 — Playwright checks (Layer 2)

**Environment limitation, worked around.** The `mcp__playwright__browser_navigate` MCP tool failed on first use: `Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome`. This sandbox has no `/opt/google/chrome`; it has a preinstalled Chromium under `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (the same path `frontend/playwright.config.ts` already points `launchOptions.executablePath` at, per that file's own comment about `cdn.playwright.dev` being blocked). I tried pointing `.mcp.json`'s playwright server at `--executable-path /opt/pw-browsers/.../chrome`; this had no effect because the MCP server process was already started for this session before the edit, so I reverted `.mcp.json` to its original content (confirmed clean via `git diff`) rather than leave an edit that did nothing. This is the same class of environment constraint recorded in `docs/fix-loops/02-e2e-job-uv-not-installed.md` — a sandbox tooling gap, not an application defect.

Instead, browser-level verification was done with the project's own `frontend/e2e/` Playwright suite (real Chromium, the same executable, run via `npx playwright test`, not the MCP tool), against the same live backend/frontend started for this evaluation:

1. **`e2e/functional.spec.ts` (Group D's committed suite, desktop-1280 project)** — exercises Group B's endpoints through the UI: login per role, ticket creation, agent claim from the workbench, a stale-version 409 surfaced as an `ErrorBanner` message, **AC-08's customer-reply-on-`PENDING_CUSTOMER`-moves-to-`OPEN`** transition, and a `CLOSED` ticket rendering read-only. Ran with `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers npx playwright test e2e/functional.spec.ts --project=desktop-1280`:
   ```
   Running 8 tests using 1 worker
     ✓ E2S4_customer_login_lands_on_my_tickets
     ✓ E2S4_agent_login_lands_on_agent_workbench
     ✓ E2S4_admin_login_lands_on_admin_console
     ✓ E2S4_customer_creates_a_ticket
     ✓ E6S1_agent_claims_the_ticket_from_the_workbench
     ✓ E6S1_invalid_status_change_shows_the_409_message
     ✓ AC-08 customer reply on pending-customer moves ticket to open
     ✓ E6S1_closed_ticket_is_read_only
   8 passed (9.9s)
   ```
   **PASS.**

2. **`PW-B-claim-reassign-note-reply`** — a short-lived, evaluator-only spec (`frontend/e2e/tmp_group_b_eval.spec.ts`, deleted immediately after this run, not committed) that exercises claim, reassign, and note-hiding specifically, since the committed suite covers claim and the AC-08 reply flow but not reassign or note-visibility through the UI. Ran with the same command against `desktop-1280`:
   ```
   Running 1 test using 1 worker
     ✓ eval_B_claim_reassign_note_reply_through_ui (3.0s)
   1 passed (4.2s)
   ```
   Screenshots captured as evidence, saved under `frontend/e2e/eval-screens/` (left in place as this run's artifacts; not part of the committed test suite):
   - `B-01-agent-claimed.png` — agent1 view right after Claim: assignee no longer "Unassigned", status `IN_PROGRESS`.
   - `B-02-agent-reassigned.png` — after reassigning to `AG-2`.
   - `B-03-agent-note-visible-to-agent.png` — agent2 view showing "Internal notes: INTERNAL-NOTE-EVAL-MARKER checked the logs", assignee `AG-2`.
   - `B-04-customer-view-no-note.png` — customer1 view of the *same* ticket (`HD-000005`): no "Internal notes" section, no "History" section, no "Actions" section — only title/id/status/priority/assignee header fields and the Reply box. The note text does not appear anywhere on the page.
   **PASS.**

## Step 3 — Architecture checks

| Check | Result | Evidence |
|---|---|---|
| layering | **PASS** | `uv run lint-imports` → "Layered architecture KEPT / Domain is pure KEPT / Contracts: 2 kept, 0 broken." (76 files, 254 dependencies analyzed) |
| typing | **PASS** | `uv run mypy src/` → "Success: no issues found in 55 source files" |
| folder_structure | **PASS** | `backend/src/` contains `api/`, `config/`, `domain/`, `repository/`, `service/`, `types/` |

## Step 4 — Backend gate

- `uv run pytest -x -q` → **270 passed**, 0 failed, coverage 99.22% (floor 80%). (Note: `uv sync` needed the `--extra dev` flag first — `pytest`/`ruff`/`mypy`/`import-linter` are declared as the `dev` optional-dependency group in `backend/pyproject.toml`, not the base `uv sync`. This is an environment-setup step, not an app defect; it is the same pattern Group A's report would have hit had it run `pytest` before `uv sync --extra dev`.)
- `uv run ruff check .` → "All checks passed!"
- `uv run mypy src/` → "Success: no issues found in 55 source files"
- `uv run lint-imports` → "Layered architecture KEPT / Domain is pure KEPT / Contracts: 2 kept, 0 broken."
- AC-id-named tests confirmed present on disk for every AC in scope: `tests/integration/test_status_transition_api.py`, `test_closed_ticket_immutable.py`, `test_closed_ticket_rejection_log.py` (AC-04); `test_claim_reassign_api.py` (AC-03); `test_notes_replies_api.py` (AC-07); `test_customer_reply_api.py`, `test_unknown_ticket_returns_404.py` (AC-08).

## Overall verdict: **PASS**

All 12 live API checks, both Playwright-layer checks (via the project's own Playwright runner, since the MCP browser tool was blocked by a sandbox Chrome-path issue), and all 3 architecture checks passed. The full backend gate (270 tests, ruff, mypy, lint-imports) is clean.

**No real application-code failure was found in Group B.** Every behavior specified in `specs/stories/sprint-2.md` and `specs/ticket-lifecycle_spec.md` for E3-S1 through E3-S4 was reproduced live: the six valid lifecycle edges, the `INVALID_TICKET_STATE` vs `TICKET_CLOSED_IMMUTABLE` split on a closed ticket, claim/reassign with append-only `Assignment` rows, stale-version `409`, internal notes hidden from customers, public replies visible, `405` on note/reply mutation attempts, and the full AC-08 customer-reply state machine including the 404-not-403 cross-customer rule. No entry was written to `docs/fix-loops/` for this group because there was nothing to record — the only issues encountered (MCP browser tool's hardcoded Chrome path, and `uv sync` needing `--extra dev`) are sandbox/tooling environment gaps, not defects in `backend/src` or `frontend/src`, and did not block completing every check through an equivalent live path.

### features.json updates made

`F005`, `F006`, `F007`, `F008`, `F013`, `F014`, `F015`, `F016`: `last_evaluated` refreshed to this run's timestamp; `passes` confirmed `true`; `failure_reason`/`failure_layer` confirmed `null`. No other fields were changed.

## Housekeeping

- Backend and frontend processes started for this verification (`uv run uvicorn ... --port 8000`, `npm run dev -- --port 5173`) were stopped after testing.
- `backend/helpdesk.db` was deleted once at the start to get a clean seeded DB for this run (synthetic seed data plus tickets `HD-000001`..`HD-000005` created during this verification). This is local dev data, not source code.
- `frontend/node_modules` did not exist at the start of this run (`vite: not found`); ran `npm install` to make the dev server runnable. This matches `package-lock.json` already in the repo; no `package.json` or lockfile edit was made.
- `backend/.venv` was missing the `dev` extra (`pytest`, `ruff`, `mypy`, `import-linter`); ran `uv sync --extra dev`. No `pyproject.toml` edit was made.
- `.mcp.json` was edited to try to point the Playwright MCP server at the sandbox's preinstalled Chromium, then reverted to its original content once it was confirmed the edit had no effect on the already-running MCP server process (verified via `git diff` showing no difference before finishing).
- `frontend/e2e/tmp_group_b_eval.spec.ts`, the temporary evaluator-only Playwright spec used for the claim/reassign/note screenshots, was deleted after the run. `frontend/e2e/eval-screens/*.png` (its screenshot output) was left in place as evidence for this report and is untracked.
- No application code under `backend/src/` or `frontend/src/` was modified.
