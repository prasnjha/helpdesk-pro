# Fix loop 04: Group D landed as one squashed commit

**Date:** 2026-10-04 (squashed commit `4ac2474`; follow-up refactor from `2195aef`)

## What failed

Group D (Sprint 4) landed as one commit, `4ac2474` `feat: complete Group D UI (agent workbench, admin console, KB pages), demo seed, CI`. It touched 36 files and added 2,435 lines, covering the backend login change, the seed script, the CI pipeline, the Playwright config and the frontend pages. The sprint's rule is small commits with the test before the feature, and this commit broke it. `claude-progress.txt` (Session 8, "Known deviations") says the same.

Component names also drifted from `specs/design/component-map.md`. The pages were named `AgentQueuePage`, `KbListPage` and `AdminConsolePage`, where the map specifies `WorkbenchPage`, `KbSearchPage` and separate admin pages, and the components were inlined rather than extracted.

## How it was detected

A review of the squashed commit, recorded in the "Known deviations" section of `claude-progress.txt`.

## The fix

The history was not rewritten. `4ac2474` is on `origin` (`origin/main` and the `claude/` branches contain it), and the project's rule is that pushed history is not rewritten, as recorded in `claude-progress.txt`. The deviation was documented, and the repayment was done as new commits:

- Red-first commits for each component and page, for example `2195aef` `test: add failing test for SlaBadge component` and `211ff46` `test: add failing test for WorkbenchPage (split from AgentQueuePage)`.
- Each one followed by a `refactor:` commit that extracted or renamed it, for example `4daca6e` and `a2c57f3`.
- They are merged through PR #7 (`1caea44`), which sits right after PR #6 (`ccefae7`) in the history.

## The lesson

If a squash is already pushed, do not rewrite it. Record the deviation where the team will see it, and repay it with small test-first commits. The squash itself is still in the history, so `docs/tdd.md` says so.
