# Architecture (solo, minimal)

- Status: APPROVED

Full rules: `.claude/architecture.md`. Requirements: `specs/brd/brd.md` Section 8. Endpoints: `specs/design/api-contracts.md`. Entities: `specs/design/data-models.md`.

## Layers

Dependencies point downward only. A layer may import from the layers it points to, never from above. The arrow reads "may import from".

```mermaid
flowchart TD
    UI["UI: frontend/src (pages, components, api client)"] --> API
    API["API: backend/src/api (routes, role checks, validation)"] --> SVC
    SVC["Service: backend/src/service (use cases, transactions, Clock)"] --> DOM
    SVC --> REPO
    DOM["Domain: backend/src/domain (state machine, SLA math, routing rules; no framework imports)"] --> TYPES
    REPO["Repository: backend/src/repository (SQLAlchemy, append-only migrations)"] --> CFG
    REPO --> TYPES
    CFG["Config: backend/src/config (settings, DB URL, env)"] --> TYPES
    TYPES["Types and models: backend/src/types (entities, enums, Clock interface, error envelope)"]
```

Rules that follow from the diagram:

- Domain rules live only in `src/domain`. They import Types, never FastAPI, SQLAlchemy or React.
- Services own transactions. Ticket insert and routing share one transaction (ASM-S7). Breach and escalation share one transaction.
- Controllers check roles (NFR-04). Services never trust a role passed without a check at the API layer.
- Only the router writes `queue_id` on create. An architecture test enforces this (NFR-08).
- SLA code uses integer minutes only, with no float type and no `/` division (NFR-01).
- Time comes from the injected Clock. No code calls the system clock directly, and no test sleeps.

## Sequence: ticket creation, SLA breach, escalation

No scheduler exists. Breach checks run on each ticket read or write (ASM-S8, `specs/escalation_spec.md`).

```mermaid
sequenceDiagram
    participant C as Customer UI
    participant API as API
    participant SVC as Ticket service
    participant DOM as Domain
    participant DB as Repository and DB
    participant A as Agent or admin UI

    C->>API: POST /api/tickets with bearer token
    API->>API: Validate body and role customer
    API->>SVC: create_ticket
    SVC->>DB: Begin transaction
    SVC->>DOM: route category to queue
    alt No rule for category
        DOM-->>SVC: RoutingRuleMissing
        SVC->>DB: Rollback
        API-->>C: 409 ROUTING_RULE_MISSING
    else Rule found
        SVC->>DB: Next HD id, insert ticket with queue and SLA policy version
        SVC->>DB: Insert ROUTED history, TIMER_STARTED x2 events
        SVC->>DB: Commit
        API-->>C: 201 status OPEN
    end

    Note over C,A: No public reply after 15 minutes (Critical response target)

    A->>API: GET /api/tickets/{id}/sla
    API->>SVC: read timers at Clock now
    SVC->>DOM: evaluate_sla(ticket, now) in integer minutes
    DOM-->>SVC: response BREACHED, breached_at = deadline
    SVC->>DB: Begin transaction
    SVC->>DB: Insert BREACHED_RESPONSE event
    SVC->>DOM: escalation target for category (Tier 2)
    SVC->>DB: Set escalated true, queue to Billing Tier 2
    SVC->>DB: Insert ESCALATED event and ESCALATED history (actor system)
    SVC->>DB: Commit
    API-->>A: 200 SLA with state BREACHED

    A->>API: GET /api/tickets/{id}/sla again
    SVC->>DOM: evaluate_sla(ticket, now)
    Note over SVC,DB: Already breached and escalated, so no new SlaEvent rows
    API-->>A: 200 SLA with state BREACHED
```

## Invariants checked by tests

- Closed tickets are immutable (NFR-08).
- Cross-customer reads return 404 (NFR-08).
- Routing cannot be bypassed (NFR-08).
- Append-only tables expose no update or delete method (NFR-02, NFR-05).
- Each timer produces at most one breach event and each ticket at most one ESCALATED event.
