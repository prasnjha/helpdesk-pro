
## Group A — 2026-10-03

- Mode: solo (generator worked directly, no sprint contract negotiation per project-manifest.json execution.default_mode).
- Stories implemented: E1-S1 (Clock, error envelope), E1-S2 (seeded users, bearer login), E1-S3 (health), E1-S4 (SLA policy v1 seed), E2-S1 (ticket table, HD-###### sequence, create service), E2-S2 (routing rules, seed teams), E2-S3 (create-ticket API with routing), E2-S4 (login page, new-ticket form, ticket list).
- Backend: FastAPI app with types -> config -> repository -> service -> api layering, plus a pure src/domain/routing module. Append-only SQL migrations (001-004) seed teams, users, routing rules and SLA policy v1. import-linter, ruff, mypy all pass.
- Frontend: Vite + React + TS with LoginPage, MyTicketsPage, NewTicketPage, AuthGuard, TicketForm, ErrorBanner, api/client.ts, state/session.ts.
- Gates: backend pytest 40 passed, coverage 99% (floor 80%); ruff/mypy/lint-imports clean. Frontend vitest 11 passed; tsc and eslint clean.
- Features closed: F001, F002, F003, F004 (AC-01, AC-02).
- Verdict: PASS. No self-healing needed.

## Group C — 2026-10-04

- Mode: solo (generator worked directly, no sprint contract negotiation).
- Stories implemented: E4-S1 (SLA policy versioning API), E4-S2 (response and resolution timers), E4-S3 (breach escalation to tier 2).
- Backend: src/domain/sla.py (integer-minute timer math), src/domain/escalation.py (tier-2 slug), src/domain/sla_policy.py (value rules); migration 006_sla.sql (timer-stop columns, append-only sla_event table); sla_policy_repository and sla_event_repository (append-only, structurally checked); src/repository/sla_repository.evaluate_and_escalate (the one function that detects and records a breach and escalates, run on every SLA read, idempotent); src/service/sla_service.py and sla_policy_service.py; GET /api/tickets/{id}/sla and the admin SLA policy router (POST/GET/PATCH/PUT/DELETE).
- Gates: backend pytest 144 passed (33 new); ruff, mypy --strict, lint-imports clean; coverage 99% (floor 80%, baseline 99%, unchanged — ratchet held).
- Features closed: F009, F010, F011, F012, F019, F020 (AC-05, AC-06, AC-10).
- Verdict: PASS. No self-healing needed.

## Group D (partial) — 2026-10-04

- Mode: solo (generator worked directly, no sprint contract negotiation).
- Stories implemented this session: E5-S1 (KB publish and CRUD API, AC-09), E6-S5 (CI pipeline).
- Backend: src/domain/kb.py (tag rules), migration 008_kb.sql (kb_article, kb_article_tag), src/repository/kb_repository.py, src/service/kb_service.py, src/api/routers/kb.py (/api/kb/articles POST/GET/GET-by-id/PUT/DELETE). Config: .github/workflows/ci.yml (backend ruff/mypy/lint-imports/pytest --cov-fail-under=80, frontend eslint/tsc/vitest, e2e Playwright job that no-ops until E6-S3 adds a config).
- Gates: backend pytest 158 passed (17 new); ruff, mypy --strict, lint-imports clean; coverage 99% (floor 80%, baseline 99%, unchanged). Frontend: 11 vitest tests, lint, typecheck all pass (untouched).
- Features closed: F017, F018 (AC-09).
- Not attempted this session: E5-S2 (KB pages UI), E6-S2 (admin console UI), E6-S1 (agent workbench UI), E6-S3 (responsive layout + Playwright suite), E6-S4 (README + seed data), E6-S6 (optional stretch notifications). These remain open for the next iteration of group D.
- Verdict: PASS for the two stories attempted. Group D as a whole is NOT complete; no self-healing was needed for what was built.

## Group D (continued) — 2026-10-04

- Mode: solo (generator worked directly, no sprint contract negotiation, per `/auto --group D --mode solo`).
- Stories implemented this session: E5-S2 (KB pages), E6-S1 (agent workbench UI), E6-S2 (admin console UI), E6-S3 (responsive layout + Playwright), E6-S4 (README quick-start + seed sample tickets), E6-S5 (frontend/e2e CI stages added on top of the prior session's backend-only pipeline).
- Backend: `POST /api/auth/login` now also returns `role` and `username` (additive field, `api-contracts.md` updated) so the UI can route by role without a `/me` call — a design gap found while implementing E6-S1/E6-S2's role-gated routes. `backend/scripts/seed_demo_tickets.py` seeds ~15 demo tickets through the real service layer (create/claim/status/reply, driven by the production `TestClock`, not raw SQL), covering all five lifecycle states plus one Billing ticket already escalated to Billing Tier 2 after a response breach; idempotent; runs only against the real `helpdesk.db`, never the per-test in-memory database, so no existing test's expectations changed.
- Frontend: `state/session.ts` now stores role/username alongside the token; `AuthGuard` takes an optional `allow` role list. New pages: `TicketDetailPage` (shared by customer/agent/admin — reply box always, notes/history/claim/reassign/status/note/publish-to-KB gated to staff), `AgentQueuePage` (queue + priority filter, worst-of response/resolution SLA state per row), `AdminConsolePage` (SLA policy editor + version history + dashboard tables), `KbListPage` (search, no editor link for customers), `KbArticlePage` (new/edit/view, no Edit/Delete for customers). `App.tsx` wires all of these behind role-gated routes. Added `src/styles/global.css` (table-scrolls-not-page at narrow widths, 100%-width form controls) imported from `main.tsx`.
- E2E: added `@playwright/test`, `playwright.config.ts` (three projects: 375/768/1280 px) and `e2e/responsive.spec.ts`. **Could not execute** in this sandbox — `npx playwright install` is blocked by the outbound allowlist (`cdn.playwright.dev` returns 403 from the agent proxy); see `.claude/state/failures.md`. The spec passes TypeScript/ESLint (gates 1-2) but is unproven end-to-end here; `features.json` F029 is marked `passes: false` for this reason, not swept under a general pass.
- CI: `.gitlab-ci.yml` gained `frontend:lint`, `frontend:typecheck`, `frontend:test` and a `frontend:e2e` stage using the official Playwright container image (so the sandbox's download restriction does not apply to a real CI runner).
- Gates: backend pytest 175 passed (17 new: login role/username test, 3 seed-script tests, 14 from prior sessions this count supersedes); ruff, mypy --strict, lint-imports clean; coverage 99% (floor 80%, baseline 99%, unchanged — ratchet held). Frontend: 26 vitest tests passed (15 new), eslint clean, tsc clean.
- Features closed: F021-F028, F030, F031 passing; F029 (Playwright execution) left `passes: false` with an honest `failure_layer`.
- Not attempted this session: E6-S6 (optional stretch — notification rows and inbox). Per `specs/stories/sprint-4.md`, "No other story depends on it, so it can be dropped without blocking" — dropped deliberately, not a failure.
- Verdict: PASS for every story's gates 1-2 (tests, lint/types) except the Playwright execution step, which is environment-blocked rather than failed. No 3-attempt self-heal was needed for any code defect this session — the one failure logged is an infrastructure/egress limitation, not a bug.
