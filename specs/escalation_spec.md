# Escalation Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-06 (Sprint 3)
- Roles: system action on breach. Agents see escalated tickets in tier-2 queues.

## 1. Purpose

When a response or resolution timer breaches, the ticket is flagged `ESCALATED` and moved to the higher-tier queue for its category. The lifecycle status is not changed. Escalation is a flag plus a queue move (A-05, A-06).

## 2. Behavior

- Trigger: a new `BREACHED_RESPONSE` or `BREACHED_RESOLUTION` SlaEvent, detected by the SLA engine (`sla-engine_spec.md`).
- Effect, in one transaction:
  - `escalated = true` on the ticket.
  - `queue_id` moves from `<Category>` to `<Category> Tier 2` (A-06). Example: Billing to `Billing Tier 2`.
  - One SlaEvent `ESCALATED` and one TicketHistory row with event `ESCALATED`, actor `system`.
  - `status` is unchanged.
- Idempotency: each timer produces at most one `BREACHED_*` event and at most one `ESCALATED` event. Repeated evaluation writes nothing new.
- If both timers breach, the ticket is escalated once. The second breach event is recorded, but the queue move does not repeat because the ticket is already in tier 2.
- Breach evaluation runs on every ticket read and every ticket write (ASM-S8). Reads of a `CLOSED` ticket never write events, because `CLOSED` tickets are immutable (NFR-08).
- A later customer reply (AC-08) or status change does not clear `escalated`.
- Agents in tier-2 queues see escalated tickets in their queue. Filter: `GET /api/agent/queues/{queue}/tickets?escalated=true`.

ASM-S8 (this spec): breach evaluation is piggybacked on reads and writes, because there is no scheduler (BRD 8.2). Each breach is therefore recorded at the first read or write after the deadline, with `breached_at` set to the exact deadline minute.

## 3. Acceptance Criteria

### AC-06 Breach flags ESCALATED and moves to the higher-tier queue

- Given Billing ticket HD-000020 with a Critical response target of 15 minutes and no public agent reply, When the ticket is read at created_at + 15 min, Then `escalated` is true, `status` is still `OPEN`, `queue` is `Billing Tier 2`, and one `BREACHED_RESPONSE` and one `ESCALATED` SlaEvent exist.
- Given Technical ticket HD-000021 in `IN_PROGRESS` with a resolution target of 480 minutes, When the ticket is read at created_at + 480 min, Then `escalated` is true, `status` is `IN_PROGRESS`, and `queue` is `Technical Tier 2`.
- Given HD-000020 is already escalated, When it is read again at created_at + 600 min, Then no new `BREACHED_RESPONSE` and no new `ESCALATED` event is written, and the row count for SlaEvent is unchanged.
- Given ticket HD-000022 with a response breach at 15 min and a resolution breach at 480 min, Then two `BREACHED_*` events exist, one `ESCALATED` event exists, and `queue` is `Billing Tier 2` with a single queue-move history row.
- Given ticket HD-000023 with a first public agent reply at created_at + 10 min and a response target of 15 min, When it is read at created_at + 60 min, Then no `BREACHED_RESPONSE` event exists and `escalated` is false.
- Given ticket HD-000024 in `PENDING_CUSTOMER` with a resolution breach, When the customer replies (AC-08), Then the status moves to `OPEN` and `escalated` remains true.
- Given a `CLOSED` ticket whose breach was recorded before closure, When it is read, Then no new SlaEvent is written.

## 4. Out of Scope

- Notification delivery on escalation (recorded as Notification rows only, A-14).
- Manual escalation by agents or admins.
- Escalation beyond one tier.
