# TDD Discipline

Every change follows red, green, refactor. Production code is written by agents only, and a test always comes first.

## The loop

1. **Red.** Write one failing test from an acceptance criterion. Name it with the AC id. Run it and confirm it fails for the expected reason.
2. **Green.** Write the smallest code that makes it pass. Run the whole suite.
3. **Refactor.** Clean up with the suite green. Run `ruff`, `mypy` and `lint-imports`.
4. Commit with the test and code together, using conventional commit messages (`test:`, `feat:`, `refactor:`).

## Rules

- No implementation before a failing test.
- Never edit a test to make it pass. Fix the code or fix the spec.
- Time-based behavior uses the injected test Clock. Tests never sleep.
- Coverage floor is 80 percent, with 100 percent of meaningful lines as the target.
- Every AC has at least one test. `/ac-coverage` reports gaps.

## Worked example: AC-06 SLA breach

*Replace the placeholders below with the real commit ids and output after Sprint 3.*

1. **Red.** Test `test_AC06_response_breach_moves_ticket_to_tier_2`: create a Billing ticket with a Critical response target of 15 minutes and no public reply, advance the test Clock by 15 minutes, read the ticket. Expect `escalated` true, status unchanged, queue `Billing Tier 2`, one `BREACHED_RESPONSE` and one `ESCALATED` event. It fails because breach evaluation does not exist yet. Commit: `<id>`.
2. **Green.** The agent adds the breach step to the single SLA evaluation function and the queue move to the escalation service. The test passes. Commit: `<id>`.
3. **More red tests.** Repeat reads write nothing new. Both timers breaching escalates once. A public reply before the deadline prevents a breach. Each one is added failing first, then made to pass.
4. **Refactor.** The agent removes duplication between the response and resolution timers. The suite stays green and `sla-monitor-agent` returns PASS.