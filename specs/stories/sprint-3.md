# Sprint 3 Stories — AC-05, AC-06, AC-10

## E4 SLA engine and policy

### E4-S1 SLA policy versioning API
- Layer: API · Group: C · Depends on: E1-S4
- Description: Admin endpoints that create policy versions and read history. Published versions are immutable. Covers AC-10.
- Acceptance criteria:
  1. Given admin posts High 45/360, When accepted, Then the response is 201 with `version=2`, and v1 is unchanged.
  2. Given a published version, When `PATCH`, `PUT`, or `DELETE` is sent, Then the response is 409 `POLICY_VERSION_IMMUTABLE` and no row changes.
  3. Given a float value, or `resolution_minutes` below `response_minutes`, Then the response is 422. Given an agent caller, Then the response is 403.

### E4-S2 Response and resolution timers
- Layer: Service · Group: C · Depends on: E2-S1, E4-S1, E3-S1
- Description: Domain functions for integer-minute elapsed time, stop rules, and timer states, exposed by `GET /api/tickets/{id}/sla`. Covers AC-05, ASM-S3, and ASM-S6.
- Acceptance criteria:
  1. Given a Critical ticket created at T0, When read at T0 + 11 min, Then the state is `ON_TRACK`. At T0 + 12 min, the state is `AT_RISK`. At T0 + 14 min 59 s, the state is `AT_RISK`. At T0 + 15 min, the state is `BREACHED`.
  2. Given an internal note at T0 + 5 min and a first public reply at T0 + 20 min, Then `response.stopped_at` is T0 + 20 min and stays at 20 minutes elapsed.
  3. Given a `PENDING_CUSTOMER` ticket, Then the resolution timer keeps running. When the ticket reaches `RESOLVED` at T0 + 200 min, Then the timer stops at 200 minutes.

### E4-S3 Breach escalation to tier 2
- Layer: Service · Group: C · Depends on: E4-S2, E2-S2
- Description: On breach, set `escalated`, move the ticket to the tier-2 queue, and write one SlaEvent and one history row per timer. Covers AC-06.
- Acceptance criteria:
  1. Given a Billing ticket whose response timer breaches at 15 minutes, When read, Then `escalated` is true, the status is unchanged, and the queue is `Billing Tier 2`.
  2. Given a ticket already escalated, When read again, Then no new SlaEvent rows are written.
  3. Given a `CLOSED` ticket with a prior breach, When read, Then no new SlaEvent rows are written.
