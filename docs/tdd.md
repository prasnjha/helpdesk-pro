# TDD Discipline

Every change follows red, green, refactor. Production code is written by agents only, and a test always comes first.

## The loop

1. **Red.** Write one failing test from an acceptance criterion. Name it with the AC id. Run it and confirm it fails for the expected reason.
2. **Green.** Write the smallest code that makes it pass. Run the whole suite.
3. **Refactor.** Clean up with the suite green. Run `ruff`, `mypy` and `lint-imports`.
4. Commit in three separate steps: the failing test first (`test:`), then the code that makes it pass (`feat:`), then the cleanup (`refactor:`).

## Rules

- No implementation before a failing test.
- Never edit a test to make it pass. Fix the code or fix the spec.
- Time-based behavior uses the injected test Clock. Tests never sleep.
- Coverage floor is 80 percent, with 100 percent of meaningful lines as the target.
- Every AC has at least one test. `/ac-coverage` reports gaps.

## Worked example: AC-06 SLA breach escalation

AC-06: when a ticket's response timer breaches, the ticket is flagged ESCALATED and moved to the Tier 2 queue of its team. The breach happens once only, and the ticket status does not change.

| Step | Commit | What happened |
|---|---|---|
| Red | `60eaea5` `test: AC-06 breach escalation to tier 2 (red)` | 16 new tests were added and failed because the code did not exist yet. They cover the Tier 2 queue names, a breach escalating the ticket, a repeat read writing no new event, both timers breaching but escalating only once, a closed ticket never being written to, and the event log having no update or delete method. |
| Green | `1b6b3b3` `feat: AC-06 breach escalation to tier 2 (green)` | The smallest code to pass them: an escalation rule (`escalation.py`), an append-only SLA event table and repository, and the breach and escalate logic. |
| Refactor | `202662b` `refactor: extract breach-recording and escalation helpers` | The same behaviour with the logic tidied into helper functions. The tests stayed green. |

Result: the full suite passes with 99 percent coverage, and `ruff`, `mypy --strict` and `lint-imports` are clean.

## Note on history

Group A and B were built before the per-AC commit rule was enforced, so their history is coarser. From Group C onward, every AC has its own red, green and refactor commits.