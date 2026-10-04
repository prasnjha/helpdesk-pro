# Knowledge deposits

Reusable rules this project learned, dated by the commit or log entry where each was recorded. Each entry names where the rule was applied. Incident detail lives in [`docs/fix-loops/`](fix-loops/README.md).

## 2026-10-03

- **Check the story before you write a live check.** A contract check that calls a route from a later sprint is a scope question. Record the deferral in the contract, not as a silent pass. Applied in `sprint-contracts/A.json` and `specs/reviews/evaluator-report.md` (Step 3), committed in `d1e9a18`. See [fix loop 03](fix-loops/03-ticket-detail-route-evaluator-finding.md).
- **Do not work around a sandbox block.** When the sandbox refused a direct SQLite write, the evaluator recorded the check as inconclusive and did not work around the block. Applied in `specs/reviews/evaluator-report.md` (Step 2), committed in `d1e9a18`.
- **Write the architecture contract test before the code it guards.** Applied in `7b0b25a` `test: add import-linter architecture contract test`, which `claude-progress.txt` (Session 3) says was written before any Group B code.
- **Append-only tables get a structural test.** Repositories for append-only tables may only insert and read, and a test checks that no update or delete method exists. Applied in `backend/tests/architecture/test_assignment_repository_append_only.py`, added in `1ae1d4a`.

## 2026-10-04

- **Check cross-origin behaviour from a real browser.** The API had no CORS middleware, so browser requests from the UI origin failed at preflight. Applied in `40d3461` (red) and `064559c` (green), with the origins set in `backend/src/config/settings.py`. See [fix loop 01](fix-loops/01-cors-blocked-browser-login.md).
- **Mark an e2e test as not passing until it has run.** `features.json` F029 stayed `passes: false` until a real run passed. Applied in `4ac2474` (F029 set to false with `failure_layer: "e2e"`) and flipped to true only in `6e20899`, after the run.
- **Treat an environment block as an environment block.** A sandbox egress block cannot be fixed by retrying, so it is logged as its own entry instead of going through the 3-attempt loop. Applied in `.claude/state/failures.md`, Group D Failure #1, committed in `4ac2474`.
- **Every command a CI script calls must be installed in that job.** Applied in `85b5f47`, which copies the backend job's uv setup into the e2e job. See [fix loop 02](fix-loops/02-e2e-job-uv-not-installed.md).
- **Only one owner starts services in CI.** Applied in `73cf067`, which lets `playwright.config.ts`'s webServer own the startup of both services.
- **Seed data goes through the service layer, not raw SQL.** Applied in `backend/scripts/seed_demo_tickets.py`, added in `4ac2474`. `claude-progress.txt` (Session 7, item 4) gives the reason: every invariant holds the same way it does for a real user.
- **Keep one commit per red, green and refactor step.** Group C follows the rule: `8a14ea3` (red), `0d6376f` and `1b6b3b3` (green), `202662b` (refactor). Group B (`1ae1d4a`), the KB API (`0017eb9`) and Group D (`4ac2474`) do not. See [fix loop 04](fix-loops/04-group-d-squashed-commit.md) and `docs/tdd.md`.
- **Get explicit approval before a change outside the agreed scope.** The CORS fix changed the backend, outside the seed-only allowance, so approval came first. Applied in `064559c`, recorded in `claude-progress.txt` (Session 8, item 3).
- **Do not rewrite pushed history. Record the deviation and repay it with test-first commits.** Applied to `4ac2474`, which is on `origin`. The record is in `claude-progress.txt` ("Known deviations") and `docs/tdd.md` ("Note on history"). The repayment is the red-first refactor series starting at `2195aef`, merged in PR #7 (`1caea44`).
- Files required by the capstone rubric (the Agent SDK script, plugin.json, hooks) are not dead code even if nothing imports them; the janitor must check the rubric before flagging.
- **Record over-length files as known exceptions instead of splitting them in a scoped cleanup.** Two source files break the 300-line rule: `backend/src/repository/ticket_repository.py` (554 lines) and `backend/src/api/routers/tickets.py` (410 lines). The `docs/sync-drift` cleanup was limited to doc fixes and dead-code removal, so both stay whole. A split moves public functions across modules and needs its own test-first refactor. Found by the janitor run in [`docs/agent-runs/janitor-agent.md`](agent-runs/janitor-agent.md) (Check 3). Status: known, open.
- **A guard hook that must prevent a change has to be PreToolUse; PostToolUse runs after the change has happened.** `protect-env.js` was registered under PostToolUse, so it ran after the `.env` write. Applied in the commit with the subject `chore: move env guard hook to PreToolUse so it runs before the write` (on `chore/env-guard-pre`; its hash is in `git log`).
