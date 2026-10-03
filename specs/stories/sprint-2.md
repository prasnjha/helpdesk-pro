# Sprint 2 Stories — AC-03, AC-04, AC-07, AC-08

## E3 Ticket lifecycle and agent actions

### E3-S1 Lifecycle state machine
- Layer: Service · Group: B · Depends on: E2-S1
- Description: Domain state machine with the six valid edges (`ticket-lifecycle_spec.md` §2), `InvalidTicketStateException`, and history writes. Covers AC-04.
- Acceptance criteria:
  1. Given each of the six valid edges, When the transition is requested, Then it returns 200 and writes one history row.
  2. Given `OPEN` to `RESOLVED`, When requested, Then `InvalidTicketStateException` maps to 409 `INVALID_TICKET_STATE` and the status is unchanged.
  3. Given a `CLOSED` ticket, When any write is attempted, Then the response is 409 `TICKET_CLOSED_IMMUTABLE` and the attempt is logged.

### E3-S2 Claim and reassign
- Layer: Service · Group: B · Depends on: E3-S1
- Description: Claim and reassign with append-only Assignment rows and the ASM-S1 status rule. Covers AC-03.
- Acceptance criteria:
  1. Given an `OPEN` ticket, When claimed, Then the response is 200, the assignee is set, the status is `IN_PROGRESS`, and one Assignment row has `from=null`.
  2. Given an assigned ticket, When reassigned, Then the response is 200, the status is unchanged, and a second Assignment row records the previous assignee in `from`.
  3. Given a stale ticket version, When a write is sent, Then the response is 409.

### E3-S3 Agent notes and public replies
- Layer: API · Group: B · Depends on: E3-S1
- Description: Internal notes and agent replies, both append-only and hidden from customers where marked. Covers AC-07.
- Acceptance criteria:
  1. Given an assigned agent, When a note is posted, Then the response is 201 and the note never appears on customer endpoints.
  2. Given an agent public reply, When posted, Then the response is 201 and the reply is visible to the customer.
  3. Given `PUT`, `PATCH`, or `DELETE` on a note or reply id, Then the response is 405 and no row changes.

### E3-S4 Customer reply transition
- Layer: API · Group: B · Depends on: E3-S1
- Description: Customer replies on own tickets. A reply on `PENDING_CUSTOMER` moves the ticket to `OPEN` in the same transaction. Covers AC-08.
- Acceptance criteria:
  1. Given a `PENDING_CUSTOMER` ticket, When the owner replies, Then the response is 201, the status is `OPEN`, and one history row is written.
  2. Given an `OPEN` or `IN_PROGRESS` ticket, When the owner replies, Then the response is 201 and the status is unchanged.
  3. Given a `RESOLVED` ticket, When the owner replies, Then the response is 409 `INVALID_TICKET_STATE`. Given another customer's ticket, the response is 404.
