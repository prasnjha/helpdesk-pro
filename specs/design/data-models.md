# Data Models (solo, minimal)

- Status: APPROVED

Source: BRD Section 9 (entity table), plus fields the feature specs require. Fields marked **(added)** come from the specs, not BRD 9.

## Entity table (BRD 9)

| Entity | Purpose | Mutability | Key fields |
|---|---|---|---|
| User | Seeded identity with role and optional team | Mutable profile; role changes recorded | `id`, `username`, `password_hash`, `role` (customer, agent, admin), `team_id?`, `active`, `display_name?` **(added, NFR-03 log redaction)** |
| Team | Queue owner (Billing, Technical, Account, and the three Tier 2 queues) | Mutable | `id`, `name` (unique), `slug` (unique, lowercase, hyphenated) **(added, API path key)**, `tier` (1 or 2) |
| Ticket | Customer issue | Mutable through services only | `id` (`HD-` + 6 digits), `title` (1 to 200), `description` (1 to 5000), `category`, `priority`, `status`, `queue_id`, `customer_id`, `assignee_id?`, `escalated` (bool, default false) **(added)**, `sla_policy_version_id` **(added, ASM-S4)**, `version` **(added, concurrency)**, `response_stopped_at?`, `resolution_stopped_at?` (UTC, nullable) **(added, E4-S2 timer stops)**, `created_at`, `updated_at` |
| TicketHistory | Each status change, route and escalation, with actor and timestamp | Append-only | `id`, `ticket_id`, `event` (ROUTED, STATUS_CHANGED, ESCALATED), `from_state?`, `to_state?`, `actor_id` or `system`, `correlation_id`, `created_at` |
| Assignment | Each claim or reassign | Append-only | `id`, `ticket_id`, `from_user_id?`, `to_user_id`, `actor_id`, `created_at` |
| TicketNote | Internal note, never shown to customers | Append-only | `id`, `ticket_id`, `author_id`, `body` (1 to 5000), `created_at` |
| TicketReply | Public reply | Append-only | `id`, `ticket_id`, `author_id`, `author_role` (customer, agent), `body` (1 to 5000), `created_at` |
| SlaPolicy | Policy version per priority | Append-only; published version immutable | `id`, `priority`, `version` (starts at 1 per priority), `response_minutes` (int ≥ 1), `resolution_minutes` (int ≥ response_minutes), `created_by`, `published_at` |
| SlaEvent | Timer start, stop, breach and escalation | Append-only | `id`, `ticket_id`, `event` (TIMER_STARTED, RESPONSE_STOPPED, RESOLUTION_STOPPED, BREACHED_RESPONSE, BREACHED_RESOLUTION, ESCALATED), `timer?` (response or resolution), `breached_at?` (UTC deadline timestamp: `created_at` of the ticket plus the target minutes), `created_at` |
| RoutingRule | Maps category to target team | Mutable by admin; plain rows, not versioned (A-07) | `category` (PK: Billing, Technical, Account), `target_queue_id` |
| KbArticle | Published knowledge article | Create and update by agent and admin; `source_ticket_id` fixed | `id`, `title` (1 to 200), `body` (1 to 5000), `source_ticket_id`, `created_by`, `created_at`, `updated_at`. Tags are not a column: they live in `kb_article_tag(article_id, tag)`, 1 to 10 lowercase tags of 1 to 30 chars each |
| Notification | Recorded notification event (no delivery, A-14) | Not built in this version (deferred) | Not built in this version (deferred). No migration exists; the fields are not in the schema |

## Constraints

- Ids: ticket ids come from a sequence, `HD-000001` upward, never reused (A-12).
- Enums: `status` in {OPEN, IN_PROGRESS, PENDING_CUSTOMER, RESOLVED, CLOSED}. `category` in {Billing, Technical, Account}. `priority` in {Critical, High, Medium, Low}. ESCALATED is a flag, not a status (A-05).
- SLA values are integers only (NFR-01). The `sla_policy` table has no UPDATE or DELETE path (NFR-05).
- Unique: `(priority, version)` on SlaPolicy. A partial unique index on `sla_event(ticket_id, timer)` WHERE `event` IN (BREACHED_RESPONSE, BREACHED_RESOLUTION), so each breach is recorded once per timer. ESCALATED has no timer and is guarded in application code. `name` and `slug` on Team.
- Foreign keys: Ticket to Team (`queue_id`), Ticket to User (`customer_id`, `assignee_id`), Ticket to SlaPolicy (`sla_policy_version_id`), KbArticle to Ticket (`source_ticket_id`).
- Indexes: `Ticket(queue_id, status, priority)`, `Ticket(customer_id)`, `SlaEvent(ticket_id, event)`, `TicketHistory(ticket_id)`, `SlaPolicy(priority, version)`.
- Timestamps stored UTC.

## Example records

```json
{"id": "HD-000020", "title": "Invoice charged twice", "category": "Billing", "priority": "Critical",
 "status": "OPEN", "queue_id": 4, "customer_id": "C-1", "assignee_id": null,
 "escalated": true, "sla_policy_version_id": 7, "version": 3,
 "created_at": "2026-10-03T09:00:00Z", "updated_at": "2026-10-03T09:15:00Z"}
```

```json
{"ticket_id": "HD-000020", "event": "BREACHED_RESPONSE", "timer": "response",
 "breached_at": "2026-10-03T09:15:00Z", "created_at": "2026-10-03T10:00:00Z"}
```
