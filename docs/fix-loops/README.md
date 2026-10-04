# Fix loops

Short records of real incidents in this project. Each one covers what failed, how it was detected, the fix, and the lesson. Every event is taken from the git log, the PR merges, `claude-progress.txt`, `.claude/state/failures.md` and `specs/reviews/`.

| # | Incident | Date |
|---|---|---|
| 01 | [Missing CORS blocked browser login](01-cors-blocked-browser-login.md) | 2026-10-04 |
| 02 | [GitHub e2e job failed because uv was not installed](02-e2e-job-uv-not-installed.md) | 2026-10-04 |
| 03 | [GET /api/tickets/{id} missing in Sprint 1 (evaluator finding)](03-ticket-detail-route-evaluator-finding.md) | 2026-10-03 |
| 04 | [Group D landed as one squashed commit](04-group-d-squashed-commit.md) | 2026-10-04 |

## Not included

These two incidents were in the brief, but the repo has no record of them, so they are not written up:

- **Sprint 3 squash, force-push blocked, and PR #4 replacing PR #3.** Group C (Sprint 3) is not squashed. Its history has separate red, green and refactor commits (`8a14ea3`, `0d6376f`, `1b6b3b3`, `202662b`). No PR #3 appears in the merge history or in any file.
- **Relative-path hooks error when the working directory changes.** No error text, commit or log entry records this. `.claude/settings.json` calls `node .claude/hooks/enforce-length-pre.js` with a relative path, but nothing records a failure from it.

The squash that the history does record is written up as fix loop 04.
