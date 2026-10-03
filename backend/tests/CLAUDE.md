# Tests

- Write the failing test first, then the code (`docs/tdd.md`).
- Every test name carries its acceptance criterion id, for example `test_AC06_breach_moves_ticket_to_tier_2`. Run `/ac-coverage` to find gaps.
- Time comes from the test Clock. Tests never sleep.
- Use synthetic seed data only.
- `tests/architecture/` holds the structural tests: closed tickets immutable, cross-customer reads blocked, routing cannot be bypassed, layering rules.
- Coverage floor 80%, report as `coverage.xml`.