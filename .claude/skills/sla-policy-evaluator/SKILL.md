---
name: sla-policy-evaluator
description: How to compute HelpDesk Pro SLA elapsed minutes, breach and AT_RISK states from stored UTC timestamps using integer arithmetic only. Use when writing or reviewing SLA timer code or SLA tests.
---

# SLA Policy Evaluator

Source of truth: `specs/sla-engine_spec.md`, `specs/admin-console_spec.md`, ASM-S4, ASM-S6, NFR-01.

## Formulas (integers only)

- `elapsed_minutes = (end - start) // timedelta(minutes=1)` where `end` is `stopped_at` if the timer stopped, otherwise `now` from the injected Clock. Never use `.total_seconds()`, `/`, `round()` or float.
- BREACHED when `elapsed_minutes >= target_minutes`.
- AT_RISK when not breached and `elapsed_minutes * 100 >= target_minutes * 80`.
- Otherwise ON_TRACK.

## Which timer stops when

- Response: stops at the first PUBLIC agent reply. Claims and internal notes do not stop it. Reaching RESOLVED also stops it if still running.
- Resolution: stops only at RESOLVED. It keeps running in PENDING_CUSTOMER.

## Policy version

A ticket stores the policy version id active for its priority at creation. Later versions apply only to later tickets. Published versions are immutable.

## Worked examples (Critical response target 15, High 60/480)

| Time since creation | Elapsed | State |
|---|---|---|
| 11 min | 11 | ON_TRACK |
| 12 min | 12 | AT_RISK |
| 14 min 59 s | 14 | AT_RISK |
| 15 min | 15 | BREACHED |
| High ticket at 14 min, target 60 | 14 | ON_TRACK |

- Internal note at 5 min, first public agent reply at 20 min: response `stopped_at` is 20 min and `elapsed_minutes` stays 20 on later reads.
- PENDING_CUSTOMER from 100 min, read at 300 min: resolution elapsed is 300, `stopped_at` null.
- RESOLVED at 200 min, read at 500 min: resolution elapsed stays 200.

## Test rules

Use the test Clock to advance time. Never sleep. Name tests with the AC id, for example `test_AC05_response_breach_at_target_minutes`.