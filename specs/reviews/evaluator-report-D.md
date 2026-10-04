# Evaluator Report — Group D (Sprint 4), retroactive verification

Date: 2026-10-04

**This contract and this evaluation are retroactive**, in the same sense as Groups B and C. Group D (`E5-S1`, `E5-S2`, `E6-S1`, `E6-S2`, `E6-S3`, `E6-S4`, `E6-S5`) was implemented and merged in solo mode across several sessions (`claude-progress.txt`, Sessions 5, 6, 7, 8, plus an unlogged follow-up refactor session visible only in `git log -- frontend/src/pages` that renamed pages to match `specs/design/component-map.md`). No `sprint-contracts/D.json` existed before this run, and no evaluator had checked Group D's UI live before now. `features.json` already showed `F017`, `F018`, `F021`-`F033` as `passes: true`, all self-reported by the solo build sessions. `sprint-contracts/D.json` was written today, after the code already existed, by reading `specs/stories/sprint-4.md`, `specs/design/api-contracts.md`, `specs/design/component-map.md`, `claude-progress.txt`, and every check below (API and Playwright) was then executed live against a freshly migrated and seeded instance of the already-built app. E6-S6 (notification rows and inbox) is confirmed **intentionally out of scope**: the story file explicitly allows dropping it, and `claude-progress.txt` Session 7 item 6 and `api-contracts.md`'s "Notifications" section both record it as deliberately not built. It is excluded from this contract and this verdict.

Mode: `local` (`project-manifest.json` verification.mode). Backend started with `cd backend && uv run uvicorn src.main:app --port 8000` against a freshly deleted/migrated `helpdesk.db`, logged to `/tmp/backend.log`. `GET /health` returned 200 on the first attempt. Demo data seeded with `cd backend && uv run python scripts/seed_demo_tickets.py` ("Seeded 15 demo tickets."). Frontend started with `cd frontend && npm run dev -- --port 5173`, reachable at `http://localhost:5173` (200).

Seeded users (password `Password123!`): `customer1`, `customer2`, `admin1`, `agent1`, `agent2` (per README's "Seed users" table).

Stories: E5-S1, E5-S2, E6-S1, E6-S2, E6-S3, E6-S4, E6-S5 (E6-S6 explicitly out of scope, see above)
Features under test: F017, F018, F021, F022, F023, F024, F025, F026, F027, F028, F029, F030, F031, F032, F033

## Sandbox note: Playwright MCP vs. the project's own runner

`mcp__playwright__browser_navigate` failed immediately with `Error: async initializeServer: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome` — the same sandbox limitation Groups B/C's evaluators hit. Worked around it by using `cd frontend && npx playwright test`, which resolves to the real preinstalled Chromium at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` per `playwright.config.ts`'s `existsSync` fallback. All Layer 2 evidence below (including screenshots) comes from that real browser, not from reading source code.

## Step 1 — API checks (Layer 1)

All requests run with `curl` against `http://localhost:8000` on the freshly seeded `helpdesk.db` above.

| Check id | Result | Evidence |
|---|---|---|
| AC-09-publish-from-resolved-ticket | **PASS** | `POST /api/kb/articles` as agent1 from `HD-000011` (RESOLVED) → `201 {"id":1,...,"source_ticket_id":"HD-000011",...}`. |
| AC-09-publish-from-open-ticket-rejected | **PASS** | Same call from `HD-000001` (OPEN) → `409 {"error":{"code":"SOURCE_TICKET_NOT_RESOLVED","message":"Ticket 'HD-000001' is not RESOLVED or CLOSED"}}`. |
| AC-09-customer-write-forbidden | **PASS** | As customer1: `POST` → `403 FORBIDDEN`; `PUT /api/kb/articles/1` → `403 FORBIDDEN`; `DELETE /api/kb/articles/1` → `403 FORBIDDEN`. Follow-up `GET /api/kb/articles/1` showed the article unchanged (same title/body/tags/updated_at as the original 201 response). |
| E6S1-agent-queue-filters | **PASS, with a documented live-read side effect** | First unfiltered `GET /api/agent/queues/billing/tickets` returned 4 rows, three already `response_state=BREACHED` but still shown in the `billing` queue. A second, otherwise-identical call returned only 1 row — the three breached tickets had been escalated (moved to `billing-tier-2`) by the per-read `evaluate_and_escalate` transaction that the `GET` itself triggers (same mechanism Group C's report documented for `GET /api/tickets/{id}/sla`). This looked like a broken filter at first and was re-verified against the now-stable `billing-tier-2` queue (all 4 tickets already escalated, membership no longer changing between reads): `priority=Critical` → exactly the 1 Critical row; `status=OPEN` → exactly the 3 OPEN rows; `status=PENDING_CUSTOMER` → exactly the 1 matching row; `escalated=true` → all 4; `priority=High` → exactly 1. All filters are correct; the earlier confusion was the documented escalation-on-read design, not a defect. |
| E6S1-agent-queue-customer-forbidden-unknown-404 | **PASS** | As customer1 → `403 FORBIDDEN`. As agent1, `GET /api/agent/queues/unknownqueue/tickets` → `404 {"error":{"code":"NOT_FOUND","message":"Queue 'unknownqueue' not found"}}`. |
| E6S1-login-returns-role-and-username | **PASS** | `POST /api/auth/login` for `customer1`/`agent1`/`admin1` each returned `{"token":...,"role":"customer"/"agent"/"admin","username":"customer1"/"agent1"/"admin1"}`. |
| E6S2-admin-dashboard | **PASS** | `GET /api/admin/dashboard?from=2020-01-01&to=2030-01-01` as admin1 → `200` with all three sections populated (`open_by_queue` across all 6 queues, `breached_by_priority` for all 4 priorities, `escalations_in_period: 4`). As agent1 → `403 FORBIDDEN`. `from=2030-01-01&to=2020-01-01` → `422 {"error":{"code":"VALIDATION_ERROR","message":"'to' must not be before 'from'"}}`. |
| E6S2-sla-policy-new-version-first-and-immutable | **PASS** | `POST /api/admin/sla-policies {"priority":"High","response_minutes":45,"resolution_minutes":360}` → `201 {"id":5,"version":2,...}`. Follow-up `GET ...?priority=High` showed `[{"version":2,...},{"version":1,"response_minutes":60,...}]` — newest first, v1 unchanged. `PATCH`/`PUT`/`DELETE /api/admin/sla-policies/versions/2` each → `409 POLICY_VERSION_IMMUTABLE`. |

## Step 2 — Playwright checks (Layer 2)

### Committed suite, run live (no modifications)

`cd frontend && npx playwright test` (all three projects: mobile-375, tablet-768, desktop-1280):

```
11 passed (16.2s)
22 skipped
0 failed
```

The 22 "skipped" are intentional: `functional.spec.ts` gates its flows to the `desktop-1280` project only (viewport doesn't change the outcome), and `responsive.spec.ts` gates each breakpoint check to its own project — so each spec file runs 3x across projects but each individual test only executes once, by design (`test.skip` guards, read and confirmed in both files).

`functional.spec.ts`'s 8 tests (login landing per role x3, create ticket, agent claim, a genuine `409 VERSION_CONFLICT` via two agents racing a stale `version`, a customer reply moving `PENDING_CUSTOMER` → `OPEN`, and a `CLOSED` ticket's read-only view) all passed live. This directly exercises F025 (claim updates in place, no reload — SPA navigation never left the page) and F033 (`StatusControl` only offered valid next states; the `CLOSED` view hid all action controls and showed "Closed tickets cannot be changed.").

`responsive.spec.ts`'s 3 tests (one per breakpoint, each asserting `scrollWidth <= innerWidth + 1` at 375px plus a pixel-diff snapshot against the committed PNGs under `frontend/e2e/snapshots/`) all passed. F029 confirmed.

### Temporary evaluator-written spec (not part of this report's deliverables; deleted before finishing)

The committed suite does not exercise the KB pages or the admin console UI (no E5-S2/E6-S2 UI coverage exists in `functional.spec.ts` or `responsive.spec.ts`). A temporary spec, `frontend/e2e/eval-group-d-temp.spec.ts`, was written and run against the live app to close that gap, then deleted. Final run (`desktop-1280` only):

```
✓ EVAL_kb_customer_search_password_and_no_editor_controls
✓ EVAL_kb_agent_saves_tags_and_sees_them
✘ EVAL_admin_policy_save_puts_new_version_first_and_dashboard_tables_render
✓ EVAL_agent_workbench_priority_filter_and_breach_badge_and_claim_no_reload
3 passed, 1 failed
```

- **EVAL_kb_customer_search_password_and_no_editor_controls — PASS.** A real article titled "How to reset your password" was published live via the API first (the demo seed creates no KB articles, per README's "Optional: demo tickets" section, and the only article created during API checks above used `password` as a *tag*, not in the title/body, which the KB search contract explicitly searches over title/body — not tags — so it correctly did not match `q=password` until a title-matching article existed). As customer1, searching "password" showed "How to reset your password" and no "New article" link; opening the article showed no Edit link or Delete button. F028 (customer side) confirmed.
- **EVAL_kb_agent_saves_tags_and_sees_them — PASS.** As agent1, `/agent/kb/new?source_ticket_id=HD-000012` prefilled the read-only source ticket field; saving with tags `billing, proration` navigated to the article detail and `[data-testid=article-tags]` showed `billing, proration`. F028 (agent side) confirmed.
- **EVAL_agent_workbench_priority_filter_and_breach_badge_and_claim_no_reload — PASS.** `/agent/queues/billing-tier-2` showed `BREACHED` in the SLA-state cell for every row; selecting `priority=Critical` narrowed 4 rows to exactly 1, and that row showed `Critical`. F026 confirmed.
- **EVAL_admin_policy_save_puts_new_version_first_and_dashboard_tables_render — PARTIAL FAIL.** The first half passed: saving a new Low 20/200 version put it first in `[data-testid=policy-row-Low]` (confirmed both by the test and by a full-page screenshot, `frontend/e2e/eval-screens/D-admin-policies.png`, which shows four Low versions with the newest, `20/200` at `2026-10-04T17:21:27...`, listed before the older `480/2880` from `2026-01-01`). The second half — asserting the admin dashboard has at least 3 `<table>` elements — failed: `tableCount` was `2`, not `>= 3`. See the real defect below.

## Real defect found: `escalations_in_period` is not rendered as a table (E6-S2 AC3)

`specs/stories/sprint-4.md` E6-S2 AC3: *"Given the dashboard, Then `open_by_queue`, `breached_by_priority`, and `escalations_in_period` are shown as tables."* `features.json`'s `F027` repeats this claim verbatim and was self-reported `passes: true`.

Live verification (admin1, `GET` then render `/admin/dashboard`, full-page screenshot `frontend/e2e/eval-screens/D-admin-dashboard.png`) shows:

- "Open tickets by queue" — a real `<table data-testid="open-by-queue-table">` with one row per queue. Correct.
- "Breached tickets by priority" — a real `<table data-testid="breached-by-priority-table">`. Correct (empty in the screenshot only because the `from`/`to` window defaulted to today-only, which has no breaches in that narrow window — a display/default-range choice, not part of this defect).
- "Escalations in period: 3" — plain text in a `<p>` element (`frontend/src/components/DashboardTables.tsx` line 49), not inside any table.

`frontend/src/components/DashboardTables.test.tsx`'s one test is literally named `"renders open_by_queue, breached_by_priority and escalations as tables"`, but its assertion for the third metric is `screen.getByText("Escalations in period: 2")` — a text match, not a table-element match — so the existing unit test's name overstates what it verifies and did not catch this gap.

This is a real, reproducible, AC-literal defect, not a sandbox limitation. Per the task instructions, **no application code was modified** to fix it. It is recorded as:

- `docs/fix-loops/05-dashboard-escalations-not-a-table.md`
- `specs/reviews/eval-failures-D.json`
- `features.json`: `F027` flipped to `passes: false`, `failure_layer: "browser"`, with a `failure_reason` pointing at the exact file/line and the fix-loop doc. (The policy-editor half of F027 — new version first in history, no edit controls on any version — is independently verified correct and is noted as such in the `failure_reason` text so a future fix only needs to touch the dashboard half.)

This is scoped narrowly: the API (`F023`) returns correct data, two of the three required tables render correctly, and no other Group D feature touches this component.

### Update (2026-10-04, later same day): defect fixed

The user asked for this specific defect to be fixed on the same branch/PR, with TDD. The fix was applied and re-verified:

- **Red:** `frontend/src/components/DashboardTables.test.tsx` was tightened to assert a real `<table>` (role `table`, a `columnheader` named "Escalations in period", a data row) for the third metric instead of matching the `<p>` text; confirmed failing against the unfixed component. Committed as `a414186` (`test: ...`).
- **Green:** `frontend/src/components/DashboardTables.tsx` now renders `escalations_in_period` as a one-column `<table data-testid="escalations-in-period-table">`, matching the other two tables' pattern and inheriting the same responsive table CSS (`global.css`, scrolls at ≤480px). `frontend/src/pages/AdminDashboardPage.test.tsx`'s same-named-but-not-asserting-a-table test was fixed the same way. Committed as `5aa9c7e` (`fix: ...`).
- **Re-verified live:** full frontend gate re-run (`npm test` 61/61, `npm run lint` clean, `npm run typecheck` clean, `npx playwright test` 11 passed/22 skipped/0 failed — unchanged, no committed visual snapshot covers the admin dashboard so no baseline needed updating) plus a temporary Playwright spec against the real running app (admin1, `GET`/render `/admin/dashboard`) confirming `escalations-in-period-table` is a genuine `<table>` with the expected header; screenshot `frontend/e2e/eval-screens/D-admin-dashboard-fixed.png`, temporary spec deleted afterward.
- `features.json`'s `F027` is back to `passes: true`. `sprint-contracts/D.json`'s `E6S2-policy-history-order-and-dashboard-tables` check, `specs/reviews/eval-failures-D.json` (added a `resolution` block), and `docs/fix-loops/05-dashboard-escalations-not-a-table.md` were all updated to record the fix and commit hashes.

**F027 is now PASS, with no outstanding real defects in Group D.**

## Step 3 — Design scoring (Layer 3, rubric-based, first UI-heavy group)

Scored against `.claude/skills/evaluation/references/scoring-rubric.md` using the screenshots in `frontend/e2e/eval-screens/D-*.png` (login, customer ticket list, agent workbench at `billing-tier-2`, admin SLA policy editor, admin dashboard, KB list) plus the existing committed responsive snapshots at 375px (`frontend/e2e/snapshots/agent-workbench-375.png`, `customer-tickets-375.png`).

| Criterion | Score | Observation |
|---|---|---|
| Visual hierarchy | 6/10 | Consistent H1/H2 scale and a visually dominant filled-blue primary button (`Sign in`, `Save new version`) on every page. Falls short of 7+: sections are separated only by heading text, not by card/whitespace grouping (e.g. the admin console's policy editor and four priority history tables sit directly stacked with no visual separation beyond an `<h3>`), and table rows have no zebra striping or hover state to aid scanning. |
| Accessibility | 7/10 | Every form input has an associated `<label htmlFor>` (confirmed by `getByLabel` succeeding in every Playwright interaction above — the project never had to fall back to CSS selectors to find a field). Buttons and links use real semantic `<button>`/`<a role=link>` elements, not clickable `<div>`s. Dark-on-light text and white-on-blue-600 buttons read as comfortably AA-contrast in the screenshots. Could not independently confirm full keyboard tab order or live-region announcements (no screen reader run in this sandbox), and there are no modals in this app so focus-trap is not applicable either way. |
| Responsiveness | 8/10 | `responsive.spec.ts` passed its `scrollWidth <= innerWidth + 1` assertion at 375px live, and the 375px snapshots (`agent-workbench-375.png`, `customer-tickets-375.png`) show the queue/ticket tables handled via `global.css`'s `@media (max-width: 480px) { table { overflow-x: auto; white-space: nowrap } }` — the table scrolls internally rather than the page, which is a stronger result than the rubric's 7-exemplar ("table does not scroll horizontally on small screens" is listed as a 7-level *gap*; here it does scroll, inside itself). No responsive nav collapse is needed or present (this is an internal B2B tool with a one-line header, not a marketing site with a nav bar), so that part of the rubric does not apply. |
| Interaction feedback | 6/10 | `ErrorBanner` surfaces specific, actionable messages (confirmed live: the two-agent stale-version scenario in `functional.spec.ts` produced a visible "updated by someone else" message, not a raw JSON dump or `alert()`). Successful actions are shown through real state changes (e.g. "Ticket created" heading, assignee text updating in place on claim) rather than a toast. No loading spinner or disabled-while-submitting state was observed on any form in the screenshots or test runs — a slow network would give the user no feedback between click and the next state change. |

All four scores are at or above `project-manifest.json`'s `design_score_threshold: 6`. None trigger the `required: true` design-check gate on their own, but the interaction-feedback and visual-hierarchy scores are the weakest and would be the first things to improve in a polish pass.

## Step 4 — CI pipeline review (E6-S5, config check only, not executed)

`.gitlab-ci.yml` was read in full, not run (no GitLab CI available in this sandbox, consistent with the task's framing of this as a config check).

- Stages: `lint → typecheck → architecture → test → e2e → review`, matching the project's actual gates (`ruff`, `mypy`, `lint-imports`, `pytest --cov-fail-under=80`) on the backend side and (`eslint`, `tsc`, `vitest`, `playwright`) on the frontend side. Coherent with `README.md`'s "Tests and linters" section — every command listed there has a matching CI job.
- `backend:test` sets `coverage: '/TOTAL.+ (\d+)%/'` and publishes `backend/coverage.xml` as a Cobertura report artifact — matches `pytest-cov`'s actual terminal output format (confirmed by this run's own `uv run pytest` output below).
- `frontend:e2e` uses the official `mcr.microsoft.com/playwright:v1.63.0-noble` image (which ships Chromium preinstalled, the same class of fix this sandbox's `/opt/pw-browsers` fallback exists for) and installs `uv` + backend deps before `npx playwright test`, since `playwright.config.ts`'s `webServer` entries boot the backend themselves via `e2e/start-backend-with-seed.sh`. This matches `docs/fix-loops/02-e2e-job-uv-not-installed.md`'s prior GitHub Actions fix for the identical problem — the GitLab job already has the fix the GitHub job needed, so this gap is closed in both pipelines.
- `claude:review` is correctly gated to only run on `merge_request_event` pipelines with `$ANTHROPIC_API_KEY` set, `allow_failure: true`, so its absence never blocks the pipeline. Matches README's "CI" section description exactly.

**Verdict: coherent, matches what the project needs.** No issues found in the YAML.

## Step 5 — Architecture checks

| Check | Result | Evidence |
|---|---|---|
| layering | **PASS** | `uv run lint-imports` → "Layered architecture KEPT / Domain is pure KEPT / Contracts: 2 kept, 0 broken." (76 files, 254 dependencies.) |
| typing | **PASS** | `uv run mypy src/` → "Success: no issues found in 55 source files." Frontend `tsc -b --noEmit` → clean, no output. |
| folder_structure | **PASS** | `backend/src/` keeps `api/config/domain/repository/service/types`. `frontend/src/pages/` now matches `component-map.md`'s naming (`WorkbenchPage`, `CustomerTicketPage`/`AgentTicketPage`, `AdminPoliciesPage`/`AdminDashboardPage`, `KbSearchPage`, `KbArticlePage`/`KbEditorPage`) per `git log --oneline -- frontend/src/pages`, which shows a refactor session (`7429568`..`68794c5`) that split and renamed the originally-squashed, inconsistently-named pages described in `claude-progress.txt`'s "Known deviations" section — that progress-log note is now stale/out of date relative to the actual repository state, which already did the renaming it asks a "future session" to do. Not treated as a failure, since the real file tree already matches the map. |

## Step 6 — Backend and frontend gates

- `cd backend && uv run pytest -x -q` → **255 passed**, 0 failed (`uv sync --extra dev` run first).
- `cd backend && uv run ruff check .` → "All checks passed!"
- `cd backend && uv run mypy src/` → "Success: no issues found in 55 source files."
- `cd backend && uv run lint-imports` → "Layered architecture KEPT / Domain is pure KEPT / Contracts: 2 kept, 0 broken."
- `cd frontend && npm test` → **61 passed** (24 test files), 0 failed.
- `cd frontend && npm run lint` → clean, 0 problems (after the temporary evaluator spec file was deleted — see Housekeeping).
- `cd frontend && npm run typecheck` → clean, no output.
- `cd frontend && npx playwright test` → **11 passed, 22 skipped (by design), 0 failed.**

## Overall verdict: **PASS — all 15 features confirmed, including F027 after its fix**

All 15 features under test (`F017`, `F018`, `F021`-`F033`) are confirmed live, independently, against a real running app and a real browser: KB publish/CRUD role and status rules, agent queue filters and role/404 gating, the dashboard API, login's role/username field, the customer/agent ticket detail split with in-place claim updates and status-transition gating, the KB search/editor/role-gating UI, the agent workbench's priority filter and BREACHED badge, the responsive layout at all three breakpoints with real Playwright snapshots, the CI pipeline's coherence, the demo seed script (15 tickets, all five lifecycle states, a Billing Tier 2 breach), CORS, and (after the fix described above) the admin dashboard rendering all three required metrics as tables.

`F027` was the one real functional/UI defect found in this group: the admin dashboard's `escalations_in_period` was shown as plain text, not a `<table>`, contradicting E6-S2 AC3's literal wording. It was scoped narrowly (one `<p>` vs. `<table>` in one component), never affected the underlying data's correctness, and never cascaded into any other feature. It was fixed test-first (red `a414186`, green `5aa9c7e`) and re-verified live; see the "Update" subsection above.

All other gates (backend pytest/ruff/mypy/lint-imports, frontend vitest/eslint/tsc/Playwright) are green.

### features.json updates made

- `F017`, `F018`, `F021`, `F022`, `F023`, `F024`, `F025`, `F026`, `F028`, `F029`, `F030`, `F031`, `F032`, `F033`: `last_evaluated` refreshed to `2026-10-04T17:24:27Z`; `passes` confirmed `true`; `failure_reason`/`failure_layer` confirmed `null`.
- `F027`: `passes` flipped `true` → `false` → **`true`** after the fix (commit `5aa9c7e`); `failure_layer`/`failure_reason` cleared back to `null`; `last_evaluated` refreshed to `2026-10-04T17:39:00Z`.
- No other fields (`id`, `title`/`description`, `story`, `group`, `category`) were changed for any feature, and no feature outside Group D's 15 ids was touched.

## Housekeeping

- Backend (`uv run uvicorn src.main:app --port 8000`) and frontend (`npm run dev -- --port 5173`) dev servers started for this verification were both stopped after testing.
- `backend/helpdesk.db` was deleted once at the start of this run for a clean seeded DB (`*.db` is gitignored; this is local dev data, not source code). It now additionally contains the demo seed (15 tickets), two real KB articles created live against the API during Layer 1/2 checks (`HD-000011`/`HD-000013` sources), a new Critical/Low SLA policy version from the live checks, and one duplicate "Eval temp: proration fix" KB article created twice (once via `curl`, once via the temporary Playwright spec) — all disposable test data in a gitignored file, not committed.
- A temporary evaluator spec, `frontend/e2e/eval-group-d-temp.spec.ts`, and a temporary screenshot-only spec, `frontend/e2e/eval-design-shots-temp.spec.ts`, were written to exercise KB/admin-console/agent-workbench UI flows and capture design-scoring evidence not covered by the committed suite. Both were **deleted** before finishing this evaluation; `git status` at the end of this run shows no untracked or modified files under `frontend/e2e/` other than the pre-existing, committed suite and the `eval-screens/` PNGs (new files: `D-admin-dashboard.png`, `D-admin-policies.png`, `D-agent-workbench.png`, `D-customer-tickets.png`, `D-kb-list.png`, `D-login.png`, added to the existing `eval-screens/` directory alongside Group B's `B-0*.png`, per the task's "reuse that dir" instruction).
- For the F027 fix re-verification (same day, later): a third temporary spec, `frontend/e2e/eval-group-d-ac3-refix.spec.ts`, was written, run against a freshly migrated+seeded backend/frontend, and **deleted** afterward, leaving one additional evidence screenshot, `frontend/e2e/eval-screens/D-admin-dashboard-fixed.png`.
- `backend/coverage.xml` shows as modified in `git status` — this is the expected regenerated-snapshot behavior described in `README.md` ("`backend/coverage.xml` is committed as a snapshot of the last test run. Pytest regenerates it...") from running `uv run pytest` during this evaluation, not an unrelated or throwaway change.
- No application code under `backend/src/` or `frontend/src/` was modified. `docs/fix-loops/05-dashboard-escalations-not-a-table.md` and `specs/reviews/eval-failures-D.json` are new documentation/evidence files, not application code.
