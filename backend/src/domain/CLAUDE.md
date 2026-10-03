# Domain layer

Pure business rules: ticket state machine, routing, SLA timers, escalation.

- No imports from FastAPI, SQLAlchemy or the api, service or repository layers.
- SLA code is integer minutes only: no float, no `/`, no `round()`, no `.total_seconds()`. A hook blocks these.
- One transition table for the six valid edges. Invalid moves raise `InvalidTicketStateException`.
- One function evaluates SLA timers: `evaluate_sla(ticket, now)`.
- Specs: `specs/ticket-lifecycle_spec.md`, `specs/sla-engine_spec.md`, `specs/escalation_spec.md`, `specs/routing_spec.md`.
- Skills: `sla-policy-evaluator`, `escalation-checker`.