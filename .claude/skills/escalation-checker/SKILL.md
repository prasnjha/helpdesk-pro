---
name: escalation-checker
description: Rules and idempotency requirements for HelpDesk Pro SLA breach escalation (flag plus queue move, once per timer). Use when writing or reviewing escalation code or AC-06 tests.
---

# Escalation Checker

Source of truth: `specs/escalation_spec.md`, A-05, A-06, ASM-S8.

## What a breach does, in one transaction

1. Record one `BREACHED_RESPONSE` or `BREACHED_RESOLUTION` SlaEvent, with `breached_at` set to the deadline timestamp (`created_at` plus the target minutes).
2. Set `escalated = true`. The lifecycle status does not change. ESCALATED is a flag, never a status.
3. Move the ticket from `<Category>` to `<Category> Tier 2` and write one TicketHistory row with event `ESCALATED`, actor `system`.
4. Write one `ESCALATED` SlaEvent.

## Idempotency

- At most one BREACHED_* event per timer and at most one ESCALATED event per ticket.
- If both timers breach, the ticket is escalated once. The second breach event is recorded, but the queue does not move again.
- Evaluating again later writes nothing new.
- `escalated` is never cleared, not by a customer reply or a status change.
- A CLOSED ticket is never written to, even by a read.

## Detection

There is no scheduler. Breach evaluation runs on every ticket read and write through the one SLA domain function. Each breach is recorded at the first read or write after the deadline.

## Test checklist (AC-06)

Response breach, resolution breach, repeat read writes nothing, both timers breach, public reply before the deadline prevents a breach, escalated stays true after a customer reply, CLOSED ticket writes nothing.