# janitor-agent run (read-only, after cleanup)

Run on branch `docs/sync-drift`, against the working tree after commits `6c8acc0` (dead code) and `863bfd6` (deposits). Read-only: no files edited, nothing installed, no pytest, no writing commands. Verdict below is the agent's own, unedited.

## Prior finding resolved?

| item | location | status | evidence |
|---|---|---|---|
| Unused imports and locals (prior run: 0 hits) | backend src and tests; frontend src | N/A (still 0 hits) | ruff F401,F841 on backend src and tests: passed. tsc noUnusedLocals and noUnusedParameters: exit 0. |
| _BREACH_EVENTS | backend/src/repository/dashboard_repository.py:14 | RESOLVED | Removed. No hits in the working tree. |
| _TERMINAL_STATUSES | backend/src/repository/dashboard_repository.py:13 | RESOLVED | Removed. No hits in the working tree. |
| get_correlation_id | backend/src/config/logging_setup.py:27 | RESOLVED | Removed. No hits in the repo. |
| scripts/ac_coverage_report.py | scripts/ac_coverage_report.py | RESOLVED | Deleted. `scripts/` now holds only dev.py and requirements.txt. |
| Test-only symbols: applied_migration_count, count_tickets, get_by_slug, has_escalation, history_events_for | backend/src/repository/db.py:51, ticket_repository.py:186 and :191, team_repository.py:19, sla_event_repository.py:65 | STILL OPEN | Referenced only by backend tests. Not in the cleanup scope (verify-then-decide items). |
| Test-only symbols: clearSession, getUsername | frontend/src/state/session.ts:76 and :70 | STILL OPEN | Referenced only by test files. Not in the cleanup scope. |
| ticket_repository.py over 300 lines | backend/src/repository/ticket_repository.py (554 lines) | ACCEPTED | Recorded as a known exception in docs/knowledge-deposits.md. |
| tickets.py over 300 lines | backend/src/api/routers/tickets.py (410 lines) | ACCEPTED | Recorded in docs/knowledge-deposits.md. |

## Check 1: Unused imports and locals

| item | location | evidence | suggested action |
|---|---|---|---|
| (none) | backend src and tests | ruff F401,F841: 0 hits | none |
| (none) | frontend src (plus e2e, per tsconfig) | tsc: exit 0 | none |

## Check 2: Dead code

Dead (no reference outside the definition):

| item | location | evidence | suggested action |
|---|---|---|---|
| LoginRequest (frontend interface) | frontend/src/api/types.ts:7 | `git grep -w` finds only the definition. Separate from the Python class of the same name in backend/src/api/routers/auth.py:17. | NEW. Delete the interface. |

Referenced only by tests:

| item | location | evidence | suggested action |
|---|---|---|---|
| applied_migration_count | backend/src/repository/db.py:51 | backend/tests/unit/test_db_and_errors.py only | verify, then delete or keep as a test helper |
| count_tickets | backend/src/repository/ticket_repository.py:186 | backend/tests/unit/test_ticket_repository.py only | verify, then delete or keep |
| get_by_slug | backend/src/repository/team_repository.py:19 | backend/tests/unit/test_team_repository.py only | verify, then delete or keep |
| has_escalation | backend/src/repository/sla_event_repository.py:65 | backend/tests/unit/test_sla_event_repository.py only | verify, then delete or keep |
| history_events_for | backend/src/repository/ticket_repository.py:191 | backend/tests/unit/test_db_and_errors.py only | verify, then delete or keep |
| clearSession | frontend/src/state/session.ts:76 | test files only | move to a test setup helper, or keep |
| getUsername | frontend/src/state/session.ts:70 | session.test.ts only | verify, then delete or keep |

Framework-referenced, verify manually (FastAPI route handlers): create_article, create_note, create_policy, create_reply, get_ticket_detail, get_ticket_sla, list_policies, list_tickets, list_tickets_for_queue, mutate_policy_version, read_dashboard, set_ticket_status, notes_are_immutable, replies_are_immutable.

## Check 3: File size

Source files of 300 lines or more:

| item | location | evidence | suggested action |
|---|---|---|---|
| ticket_repository.py | backend/src/repository/ticket_repository.py | 554 lines | ACCEPTED (docs/knowledge-deposits.md) |
| tickets.py | backend/src/api/routers/tickets.py | 410 lines | ACCEPTED (docs/knowledge-deposits.md) |

Frontend source: none at 300 lines or more. Largest is AgentTicketPage.tsx at 225 lines.

Outside src (not covered by the prior run):

| item | location | evidence | suggested action |
|---|---|---|---|
| seed_demo_tickets.py | backend/scripts/seed_demo_tickets.py | 359 lines | NEW. Split, or record as a known exception. |

Tests over 300 lines:

| item | location | evidence | suggested action |
|---|---|---|---|
| test_kb_articles_api.py | backend/tests/integration/test_kb_articles_api.py | 361 lines | optional split |

## Check 4: Dead files

(none). Every backend src module is imported. Every frontend non-test module is imported by path. scripts/dev.py and scripts/requirements.txt are referenced. backend/scripts/seed_demo_tickets.py is referenced 7 times, including by tests.

## Summary counts

- Prior findings: 4 RESOLVED (3 dead symbols and the script), 2 ACCEPTED (over-length src files), 7 STILL OPEN (test-only symbols, outside this cleanup's scope).
- Check 1: 0 ruff hits, 0 tsc hits.
- Check 2: 1 dead (LoginRequest, new), 7 test-only, 14 framework-referenced.
- Check 3: 2 source files over 300 lines (both ACCEPTED), 1 script over 300 lines (new), 1 test file over 300 lines.
- Check 4: 0 dead files.

VERDICT: CLEANUP NEEDED (the new LoginRequest and seed_demo_tickets.py items are open; the original findings are resolved)
