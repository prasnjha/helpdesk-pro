# janitor-agent run (read-only)

Run once against the repo, by a general-purpose agent following `.claude/agents/janitor-agent.md`. Nothing was edited, and no pytest or installs were run. Findings are recorded only; no application code was changed.

Commands used:
- Backend: `cd backend && uv run --no-sync ruff check --no-cache --select F401,F841 src tests`. `--no-sync` was added so `uv run` cannot write the venv. Result: passed, exit 0.
- Frontend: `cd frontend && ./node_modules/.bin/tsc -p tsconfig.json --noEmit --noUnusedLocals --noUnusedParameters`. Result: no hits, exit 0.
- Dead code: `git grep` for each top-level symbol across backend, frontend and scripts, excluding the definition and test files.
- File size: `wc -l` over tracked `.py`, `.ts` and `.tsx` files.

## Check 1: Unused imports and locals

| item | location | evidence | suggested action |
|---|---|---|---|
| (none) | backend src and tests | ruff F401/F841: 0 hits | none |
| (none) | frontend src (plus e2e, as included by tsconfig) | tsc unused-locals/params: 0 hits | none |

## Check 2: Dead code

Dead (no reference outside the definition):

| item | location | evidence | suggested action |
|---|---|---|---|
| _BREACH_EVENTS | backend/src/repository/dashboard_repository.py:14 | only the definition | delete |
| _TERMINAL_STATUSES | backend/src/repository/dashboard_repository.py:13 | only the definition | delete |
| get_correlation_id | backend/src/config/logging_setup.py:27 | no references, tests included | delete, or verify it is not meant for log formatters |

Referenced only by tests (zero non-test references):

| item | location | evidence | suggested action |
|---|---|---|---|
| applied_migration_count | backend/src/repository/db.py:51 | only backend/tests/unit/test_db_and_errors.py | verify, then delete or keep as test-only helper |
| count_tickets | backend/src/repository/ticket_repository.py:186 | only backend/tests/unit/test_ticket_repository.py | verify, then delete or keep |
| get_by_slug | backend/src/repository/team_repository.py:19 | only backend/tests/unit/test_team_repository.py | verify, then delete or keep |
| has_escalation | backend/src/repository/sla_event_repository.py:65 | only backend/tests/unit/test_sla_event_repository.py | verify, then delete or keep |
| history_events_for | backend/src/repository/ticket_repository.py:191 | only backend/tests/unit/test_db_and_errors.py | verify, then delete or keep |
| clearSession | frontend/src/state/session.ts:76 | used only by test files | likely a test helper in production code; consider moving it into setupTests |
| getUsername | frontend/src/state/session.ts:70 | only session.test.ts | verify, then delete or keep |

Framework-referenced, verify manually (FastAPI route handlers, not dead): create_article, create_note, create_policy, create_reply, get_ticket_detail, get_ticket_sla, list_policies, list_tickets, list_tickets_for_queue, mutate_policy_version, read_dashboard, set_ticket_status, notes_are_immutable, replies_are_immutable.

Counts: 3 dead, 7 test-only, 14 framework-referenced.

## Check 3: File size

Source files of 300 lines or more:

| item | location | evidence | suggested action |
|---|---|---|---|
| ticket_repository.py | backend/src/repository/ticket_repository.py | 554 lines | split |
| tickets.py | backend/src/api/routers/tickets.py | 410 lines | split |

Frontend source: none over 300. Largest is AgentTicketPage.tsx at 225 lines.

Tests over 300 lines (separate section, not a source violation):

| item | location | evidence | suggested action |
|---|---|---|---|
| test_kb_articles_api.py | backend/tests/integration/test_kb_articles_api.py | 361 lines | optional split |

Counts: 2 source files over 300, 1 test file over 300. 111 tracked files were counted.

## Check 4: Dead files

| item | location | evidence | suggested action |
|---|---|---|---|
| ac_coverage_report.py | scripts/ac_coverage_report.py | No tracked file references it except its own usage docstring. | verify manually; the ac-coverage skill may run it outside tracked files |

The check matches by basename, so it is approximate. backend/scripts/ was out of scope and was not checked.

## Summary counts

- Check 1: 0 ruff hits, 0 tsc hits
- Check 2: 3 dead, 7 test-only, 14 framework-referenced
- Check 3: 2 source files over 300 lines, 1 test file over 300 lines
- Check 4: 1 candidate

VERDICT: CLEANUP NEEDED
