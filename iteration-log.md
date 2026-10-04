
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
