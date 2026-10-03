# Ticket Lifecycle Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-04 (Sprint 2), AC-08 (Sprint 2)
- Roles: `agent` (and `admin`) change status. `customer` replies on own tickets. Customers get 403 on the status endpoint.

## 1. Purpose

A ticket's status follows one enforced lifecycle. Agents move work forward. A customer reply on a pending ticket returns it to open, so agents see that the customer has answered. Every other move is refused.

## 2. Behavior

- States: `OPEN`, `IN_PROGRESS`, `PENDING_CUSTOMER`, `RESOLVED`, `CLOSED`.
- Valid edges, exactly these six:

| From | To | Actor | Notes |
|---|---|---|---|
| `OPEN` | `IN_PROGRESS` | agent | Also set by claim (`agent-workbench_spec.md`, ASM-S1) |
| `IN_PROGRESS` | `PENDING_CUSTOMER` | agent | Agent asks the customer for information |
| `PENDING_CUSTOMER` | `RESOLVED` | agent | Agent resolves after the customer responds |
| `RESOLVED` | `CLOSED` | agent | Closure |
| `PENDING_CUSTOMER` | `OPEN` | customer | Customer reply (AC-08) |
| `IN_PROGRESS` | `RESOLVED` | agent | Documented extension (BRD 11.1) |

- Endpoint: `POST /api/tickets/{id}/status` with `{to_status}`. Success 200 with the new status.
- Each valid change writes one TicketHistory row: from-state, to-state, actor, UTC timestamp, correlation id.
- Any other move returns 409 `INVALID_TICKET_STATE`. Nothing changes and no history row is written.
- `CLOSED` is terminal. Any other write to a closed ticket returns 409 `TICKET_CLOSED_IMMUTABLE` and is logged with the correlation id.
- Customer reply: `POST /api/tickets/{id}/replies` with `{body}`, on own tickets only. The reply is stored with `author_role=customer`.
  - On `PENDING_CUSTOMER`: the reply and the move to `OPEN` commit in one transaction.
  - On `OPEN` or `IN_PROGRESS`: the reply is stored and the status is unchanged (A-18).
  - On `RESOLVED` or `CLOSED`: rejected with 409 `INVALID_TICKET_STATE`. No reply row is written (A-17).

## 3. Acceptance Criteria

### AC-04 Enforced lifecycle

- Given a ticket in each of the six valid edges (Section 2), When an agent requests that transition, Then the response is 200, the status changes, and one TicketHistory row records from-state, to-state, actor, and timestamp.
- Given an `OPEN` ticket, When an agent requests `RESOLVED`, Then the response is 409 with code `INVALID_TICKET_STATE`, the status is unchanged, and no history row is written.
- Given a `CLOSED` ticket, When any status transition is requested, Then the response is 409 with code `INVALID_TICKET_STATE`.
- Given a `CLOSED` ticket, When any other write is attempted, Then the response is 409 with code `TICKET_CLOSED_IMMUTABLE` and the attempt is logged with the correlation id.
- Given a customer calls `POST /api/tickets/{id}/status`, Then the response is 403.

### AC-08 Customer reply moves PENDING_CUSTOMER back to OPEN

- Given ticket HD-000010 owned by C-1 in `PENDING_CUSTOMER`, When C-1 calls `POST /api/tickets/HD-000010/replies` with `body="Attached the invoice."`, Then the response is 201, a TicketReply with `author_role=customer` exists, the status is `OPEN`, and one TicketHistory row records `PENDING_CUSTOMER` to `OPEN` with actor C-1. The reply insert and status change commit in one transaction.
- Given ticket HD-000011 owned by C-1 in `OPEN` or `IN_PROGRESS`, When C-1 replies, Then the response is 201, the reply is stored, and the status is unchanged (A-18).
- Given ticket HD-000012 owned by C-1 in `RESOLVED` or `CLOSED`, When C-1 replies, Then the response is 409 with code `INVALID_TICKET_STATE`, and no reply row exists (A-17).
- Given ticket HD-000013 owned by C-2, When C-1 replies on HD-000013, Then the response is 404, no row is written, and an audit log entry with the correlation id is recorded.

## 4. Out of Scope

- Reopening a `RESOLVED` ticket (A-17).
- Status changes by customers.
- Status changes triggered by SLA events. `ESCALATED` is a flag, not a status (A-05, `escalation_spec.md`).
