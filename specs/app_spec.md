# HelpDesk Pro — Root Specification

- Status: APPROVED
- Sources: `specs/brd/brd.md` (approved 2026-10-03), capstone brief BC-AINE-007 Sections 5 and 6.
- Rule: the spec is the source of truth. If spec and code disagree, the spec wins.
- Feature specs: `specs/ticket-intake_spec.md`, `specs/routing_spec.md`, `specs/ticket-lifecycle_spec.md`, `specs/agent-workbench_spec.md`, `specs/sla-engine_spec.md`, `specs/escalation_spec.md`, `specs/knowledge-base_spec.md`, `specs/admin-console_spec.md`.
- Stories: `specs/stories/` (one file per sprint) and `specs/stories/dependency-graph.md`. Features: `features.json`.

## 1. Purpose

HelpDesk Pro is a web support-ticketing and SLA platform for a B2B SaaS company. Customers file tickets through a web form. A rules-based router places each ticket in a team queue. Agents claim, reassign, note, and reply. Tickets move through an enforced lifecycle. An SLA engine tracks response and resolution timers in integer minutes and escalates breaches. Agents publish resolved tickets to a knowledge base. Admins edit versioned SLA policies without code changes. All data is synthetic.

## 2. Scope

In scope: the ten functional ACs (Sections 5 and 7), NFR-01 to NFR-08, seed data (BRD A-16), README quick-start, and the three roles.

Out of scope: email intake, WebSocket or chat, multi-channel intake, ML routing, real SSO, production deployment, real file storage, real notification delivery, business-hours SLA calendars. See BRD Section 12.

## 3. Roles

| Role | Scope |
|---|---|
| `customer` | Creates and reads own tickets, replies on own tickets, reads published KB. |
| `agent` | Works all queues, claims, reassigns, changes status, notes, replies, manages KB. |
| `admin` | All agent rights, plus SLA policies, routing rules, teams and agents, dashboard. Admin does not bypass the state machine or immutability. |

Roles are enforced in controllers (NFR-04). A customer who requests another customer's ticket receives 404.

## 4. Domain Rules (summary)

- Lifecycle: `OPEN` to `IN_PROGRESS`; `IN_PROGRESS` to `PENDING_CUSTOMER`; `PENDING_CUSTOMER` to `RESOLVED`; `RESOLVED` to `CLOSED`; `PENDING_CUSTOMER` to `OPEN` (customer reply); `IN_PROGRESS` to `RESOLVED` (documented extension). Any other transition raises `InvalidTicketStateException` (HTTP 409, code `INVALID_TICKET_STATE`).
- `ESCALATED` is a flag, not a status (BRD A-05).
- Categories: Billing, Technical, Account (A-01). Priorities: Critical, High, Medium, Low (A-11).
- All SLA values are integer minutes (NFR-01). Timestamps are UTC.
- Append-only tables: ticket history, assignments, notes, replies, SLA events, SLA policy versions, notifications (NFR-02, NFR-05).

## 5. Acceptance Criteria

The Given-When-Then criteria live in the feature specs listed in Section 7, not here. Each AC has one owning spec. AC-03 and AC-07 are in `specs/agent-workbench_spec.md`. AC-04 and AC-08 are in `specs/ticket-lifecycle_spec.md`.

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | SLA arithmetic uses integer minutes. No float type in SLA code. |
| NFR-02 | History, notes, assignments, and SLA events are append-only. |
| NFR-03 | Email, phone, and name patterns in ticket bodies are redacted in logs. |
| NFR-04 | Role checks at the controller layer. |
| NFR-05 | Migrations and SLA policy versions are append-only. |
| NFR-06 | Structured JSON logs with `X-Correlation-Id` on every request. |
| NFR-07 | `GET /health` returns 200 within 1 second of startup. |
| NFR-08 | Architecture tests: closed tickets immutable, cross-customer reads blocked, routing cannot be bypassed. |

Error body for all 4xx and 409 responses: `{"error": {"code": "<STABLE_CODE>", "message": "<text>"}}`.

| Code | HTTP | Meaning |
|---|---|---|
| `UNAUTHORIZED` | 401 | No token, or the token is invalid. |
| `INVALID_CREDENTIALS` | 401 | Wrong username or password, or a deactivated user. |
| `FORBIDDEN` | 403 | The caller's role is not allowed for this action. |
| `NOT_FOUND` | 404 | Unknown id, or a ticket the customer does not own (no existence leak). |
| `METHOD_NOT_ALLOWED` | 405 | PUT, PATCH, or DELETE sent to a note or reply id. |
| `VALIDATION_ERROR` | 422 | A field fails validation. The message names the field. |
| `VERSION_CONFLICT` | 409 | A write carries a stale `version`. |
| `ROUTING_RULE_MISSING` | 409 | No routing rule exists for the ticket's category. |
| `INVALID_TICKET_STATE` | 409 | Transition not in the valid set, or a customer reply on a RESOLVED or CLOSED ticket. |
| `TICKET_CLOSED_IMMUTABLE` | 409 | Write attempted on a CLOSED ticket. |
| `SOURCE_TICKET_NOT_RESOLVED` | 409 | KB article source ticket is not RESOLVED or CLOSED. |
| `POLICY_VERSION_IMMUTABLE` | 409 | Attempt to change or delete a published SLA policy version. |

## 7. Traceability

| AC | Criterion (short) | Owning spec | Sprint |
|---|---|---|---|
| AC-01 | Create ticket, OPEN, auto id | `ticket-intake_spec.md` | 1 |
| AC-02 | Category routing to 3 teams | `routing_spec.md` | 1 |
| AC-03 | Claim and reassign, immutable history | `agent-workbench_spec.md` | 2 |
| AC-04 | Enforced lifecycle | `ticket-lifecycle_spec.md` | 2 |
| AC-05 | Response and resolution timers | `sla-engine_spec.md` | 3 |
| AC-06 | Breach flags ESCALATED, moves to tier 2 | `escalation_spec.md` | 3 |
| AC-07 | Internal note and public reply | `agent-workbench_spec.md` | 2 |
| AC-08 | Customer reply moves PENDING_CUSTOMER to OPEN | `ticket-lifecycle_spec.md` | 2 |
| AC-09 | KB publish, CRUD for agent and admin | `knowledge-base_spec.md` | 4 |
| AC-10 | Versioned SLA policy per priority | `admin-console_spec.md` | 3 |

## 8. Sprint Plan

Each sprint closes only the ACs listed. Enablers that are not ACs are listed separately. Stories for each sprint are in `specs/stories/`.

| Sprint | ACs | Notes |
|---|---|---|
| 1 | AC-01, AC-02 | Enablers: bearer-token login for seeded users (A-08, ASM-S2), injectable Clock (A-20), health endpoint, error envelope, ticket table and HD- id sequence, routing rules and seed teams, seed SLA policy v1 for each priority (ASM-S4), minimal login page and new-ticket form so Playwright can drive AC-01 and AC-02. Tickets are never created without a queue (NFR-08). |
| 2 | AC-03, AC-04, AC-07, AC-08 | Lifecycle state machine, claim and reassign, notes and replies, customer reply transition. |
| 3 | AC-05, AC-06, AC-10 | Timers and escalation. AC-10 adds policy versions on top of the Sprint 1 seed. |
| 4 | AC-09 | KB publish. Remaining UI: agent workbench, KB pages, admin pages, responsive layout. README quick-start with seed data. CI. Optional stretch: notifications (E6-S6). |

## 9. Assumptions

BRD Section 13 (A-01 to A-20) applies unchanged. Additional assumptions from this spec set:

| ID | Assumption |
|---|---|
| ASM-S1 | Claiming an `OPEN` ticket moves it to `IN_PROGRESS` in the same transaction. Reassign does not change status. |
| ASM-S2 | Login and bearer tokens are built in Sprint 1 as an enabler for AC-01. They have no AC of their own. |
| ASM-S3 | A ticket reaching `RESOLVED` stops any running response timer that has not yet stopped. |
| ASM-S4 | Each ticket snapshots the SLA policy version active at creation. Later versions apply only to tickets created after them. |
| ASM-S5 | Field limits: title 1 to 200 characters; description and reply body 1 to 5000 characters. |
| ASM-S6 | `AT_RISK` means not breached and `elapsed_minutes * 100 >= target_minutes * 80`, using integer math. |
| ASM-S7 | Routing and the ticket insert share one transaction. A failed route leaves no ticket (`routing_spec.md`). |
| ASM-S8 | Breach evaluation runs on every ticket read and write, because there is no scheduler. Each breach is recorded at the first read or write after the deadline, with `breached_at` set to the deadline timestamp, the ticket's `created_at` plus the target minutes in UTC (`escalation_spec.md`). |

## 10. Testing Conventions

- Every AC has at least one test whose name contains its id, for example `test_AC05_response_breach_at_target_minutes`.
- Time is injected through Clock. Tests never sleep.
- Unit tests cover the domain layer without FastAPI, SQLAlchemy, or React imports.
- Coverage floor is 80%. Target is 100% of meaningful lines.
