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

- Domain rules live only in `src/domain`. They import Types only. import-linter forbids domain imports of `src.api`, `src.service`, `src.repository`, `fastapi` and `sqlalchemy`. `src.config` is not restricted by that contract.
- Services own transactions. Ticket insert and routing share one transaction (ASM-S7). Breach and escalation share one transaction.
- Controllers check roles (NFR-04). Services never trust a role passed without a check at the API layer.
- Only the router writes `queue_id` on create (NFR-08). No architecture test currently enforces this.
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
        SVC->>DB: Insert ROUTED history (no SlaEvent rows at create in this build)
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

## Logging and PII (NFR-03, NFR-06)

- **Format.** Every log line is one JSON object: `timestamp` (UTC), `level`, `logger`, `message`, `correlation_id`, plus structured fields such as `method`, `path`, `status` and `duration_ms`. Set in `backend/src/config/logging_setup.py` from `LOG_LEVEL` (default `INFO`). uvicorn's loggers use the same handler; `uvicorn.access` is held at WARNING because the request line replaces it.
- **Correlation id.** `backend/src/api/correlation_middleware.py` reuses a well-formed incoming `X-Correlation-Id` or generates one, stores it in a context variable, and returns it on every HTTP response. The header is exposed to browsers through CORS.
- **Request line.** One `helpdesk.request` line per HTTP request with method, path (no query string), status and duration. Request and response bodies are never read or logged.
- **Redaction.** `backend/src/config/log_redaction.py` runs as a handler filter, so it covers every logger. It masks, in order:
  1. email addresses as `[REDACTED_EMAIL]`;
  2. phone numbers (10 to 15 digits with common separators) as `[REDACTED_PHONE]`;
  3. known names from `users.display_name` (full, first and last name, case-insensitive, whole words) as `[REDACTED_NAME]`;
  4. names after a greeting or sign-off (`Hi`, `Hello`, `Dear`, `Regards`, `Thanks`, ...) and after `my name is` or `I am`;
  5. `body`, `description`, `subject` and `title` fields on a record are replaced with `[REDACTED]`.
- **Ticket text.** Ticket subject and body reach a log line only through `log_ticket_content` in `backend/src/config/ticket_logging.py`. It redacts first and keeps at most 200 body characters.
- **Known names.** `refresh_known_names` (`backend/src/service/known_names_service.py`) loads names at startup. Call it again after any user row is added or renamed. The app has no create-user path yet, so nothing calls it at runtime.

**Known limit.** A free-text name is not masked when it is not in the users table and has no greeting, sign-off or "my name is" / "I am" pattern. For example, "Ask Oluwaseun about the refund" passes through unmasked. The name rules are deterministic and do not use an NER model, so they trade recall for predictability. Capitalised words in a greeting are masked unless they appear on the stop list in `log_redaction.py`.
