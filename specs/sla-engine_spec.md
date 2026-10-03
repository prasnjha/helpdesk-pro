# SLA Engine Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-05 (Sprint 3)
- Roles: system computes timers. Agents and customers read them. Admin owns policy values (see `admin-console_spec.md`).

## 1. Purpose

Each ticket has two timers measured in integer minutes: a response timer and a resolution timer. Timers are computed on read from stored UTC timestamps through one domain function. There is no scheduler or background job (BRD 8.2). Breaches are detected and recorded once.

## 2. Behavior

- Timer start: both timers start at `created_at` (AC-05).
- Response timer stops at the first PUBLIC agent reply (A-02). Claims and internal notes do not stop it. Reaching `RESOLVED` also stops it if no public reply has occurred (ASM-S3).
- Resolution timer stops only when the ticket reaches `RESOLVED` (A-03). It keeps running in `PENDING_CUSTOMER`.
- Targets come from the policy version snapshotted at creation (ASM-S4): `response_minutes` and `resolution_minutes` for the ticket's priority.
- Integer arithmetic: `elapsed_minutes = (now - start) // timedelta(minutes=1)`. No float operation appears in SLA code (NFR-01, metric M3).
- Breach: `elapsed_minutes >= target_minutes`. A breach is recorded once per timer.
- States reported: `ON_TRACK`, `AT_RISK` (ASM-S6), `BREACHED`.
- Endpoint: `GET /api/tickets/{id}/sla`. Response 200:

```json
{"response": {"target_minutes": 60, "elapsed_minutes": 14, "state": "ON_TRACK", "stopped_at": null},
 "resolution": {"target_minutes": 480, "elapsed_minutes": 14, "state": "ON_TRACK", "stopped_at": null}}
```

- Visibility: customer sees own ticket's SLA block. Agents see all. Admin sees all.
- `SlaEvent` rows (append-only): `TIMER_STARTED`, `RESPONSE_STOPPED`, `RESOLUTION_STOPPED`, `BREACHED_RESPONSE`, `BREACHED_RESOLUTION`.

## 3. Acceptance Criteria

### AC-05 Timers start on creation; resolution runs until RESOLVED

- Given policy High with `response_minutes=60` and `resolution_minutes=480` at T0, When a High ticket is created at T0, Then two SlaEvent rows `TIMER_STARTED` exist, one per timer, both with start T0, and the response target is 60 and the resolution target is 480.
- Given a Critical ticket created at T0 with response target 15, When `GET /api/tickets/{id}/sla` runs at T0 + 14 min 59 s, Then `response.elapsed_minutes` is 14 and `state` is `ON_TRACK`. When it runs at T0 + 15 min 0 s, Then `elapsed_minutes` is 15 and `state` is `BREACHED`.
- Given a ticket with an internal note at T0 + 5 min and its first PUBLIC agent reply at T0 + 20 min, Then the response timer shows `stopped_at` = T0 + 20 min and `elapsed_minutes` = 20. The note at T0 + 5 min did not stop it. Reading at T0 + 60 min still shows 20.
- Given a ticket in `PENDING_CUSTOMER` at T0 + 100 min, When it is read at T0 + 300 min, Then `resolution.elapsed_minutes` is 300 and `stopped_at` is null.
- Given a ticket that reaches `RESOLVED` at T0 + 200 min, When it is read at T0 + 500 min, Then `resolution.elapsed_minutes` is 200 and `stopped_at` is T0 + 200 min.
- Given the SLA domain module, When the static check runs, Then no `float` annotation, float literal, or `/` division operator appears in `src/domain/sla` (metric M3).

## 4. Out of Scope

- Business-hours calendars (A-13). Timers use wall-clock minutes 24x7.
- Escalation actions on breach. See `escalation_spec.md`.
- Admin policy editing. See `admin-console_spec.md`.
