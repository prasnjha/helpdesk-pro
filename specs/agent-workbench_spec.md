# Agent Workbench Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-03 (Sprint 2), AC-07 (Sprint 2)
- Roles: `agent`, and `admin` (all agent rights). Customers receive 403 on every endpoint here.

## 1. Purpose

Agents take ownership of tickets, hand them to colleagues, and communicate about them. Every claim, reassignment, note, and reply is recorded. Nothing recorded can be edited or deleted afterward.

## 2. Behavior

- Claim: `POST /api/tickets/{id}/claim`. Sets the assignee to the caller. If the status is `OPEN`, it moves to `IN_PROGRESS` in the same transaction (ASM-S1). Writes one Assignment row with `from` set to the previous assignee, or null.
- Reassign: `POST /api/tickets/{id}/reassign` with `{assignee_id}`. The target must be an active agent. The status does not change (ASM-S1). Writes one Assignment row.
- Assignment rows are append-only. No update or delete method exists for them (NFR-02).
- Concurrency: writes carry the ticket version. A stale version returns 409 (BRD 11.8).
- Internal note: `POST /api/tickets/{id}/notes` with `{body}`, 1 to 5000 characters (ASM-S5). Notes are never returned on customer endpoints.
- Agent public reply: `POST /api/tickets/{id}/replies` with `{body}` and `author_role=agent`. The first public agent reply stops the response timer (A-02, `sla-engine_spec.md`).
- Notes and replies are append-only. `PUT`, `PATCH`, and `DELETE` on a note or reply id return 405.
- Ticket detail: `GET /api/tickets/{id}` serves agents and admins for any ticket. It returns all replies (public and internal), notes, history, and assignments (the append-only Assignment rows, oldest first). Customers never receive notes, history, or assignments.
- Queue listing: `GET /api/agent/queues/{queue}/tickets`, where `{queue}` is the team slug (`billing`, `billing-tier-2`, and so on). Filters are `priority`, `status`, and `escalated`. Responses include the queue's slug and name.
- Writes to a `CLOSED` ticket follow `ticket-lifecycle_spec.md`.
- Notifications: an agent's public reply and any status change create a customer notification row (optional stretch story E6-S6). Agents receive no notification rows in this build.

## 3. Acceptance Criteria

### AC-03 Claim and reassign with immutable history

- Given an `OPEN` ticket HD-000040 and agent G-1, When G-1 calls `POST /api/tickets/HD-000040/claim`, Then the response is 200, the assignee is G-1, the status is `IN_PROGRESS` (ASM-S1), and one Assignment row exists with `from=null`, `to=G-1`, actor G-1, and a UTC timestamp.
- Given HD-000040 is assigned to G-1, When agent G-2 calls `POST /api/tickets/HD-000040/reassign` with `assignee_id=G-2`, Then the response is 200, the status is unchanged, and a second Assignment row exists with `from=G-1`, `to=G-2`, actor G-2.
- Given the Assignment repository, When code is inspected or the architecture test runs, Then no update or delete method exists for Assignment rows.
- Given customer C-1 calls claim on HD-000040, Then the response is 403 and no row is written.
- Given two agents claim the same ticket with the same version, Then the second request receives 409 (optimistic version check).

### AC-07 Internal note and public reply, append-only

- Given agent G-1 assigned to HD-000050 in `IN_PROGRESS`, When G-1 calls `POST /api/tickets/HD-000050/notes` with `body="Checked refund log"`, Then the response is 201 and one TicketNote row exists.
- Given a note exists, When customer C-1 (owner) reads HD-000050 through any customer endpoint, Then the note body never appears in the response.
- Given G-1 calls `POST /api/tickets/HD-000050/replies` with `body="We are checking this now."`, Then the response is 201, the TicketReply is visible to the customer, and if it is the first public agent reply, the response SLA stops (AC-05).
- Given any note or reply id, When a PUT, PATCH, or DELETE is sent, Then the response is 405 and no row changes.
- Given customer C-1 calls the notes endpoint, Then the response is 403.

## 4. Out of Scope

- Attachments (metadata only, A-15).
- Editing or deleting notes or replies.
- Notification delivery (recorded as Notification rows only, A-14).
