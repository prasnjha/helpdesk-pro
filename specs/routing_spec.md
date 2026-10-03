# Routing Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-02 (Sprint 1)
- Roles: routing is a system action. Admin edits rules. Agents and customers read the result.

## 1. Purpose

Every new ticket is placed in exactly one team queue at creation, based on its category. Routing is rules-based. Rules are data rows that an admin can edit, not code. A ticket cannot exist without a queue (NFR-08).

## 2. Behavior

- Seed rules (`RoutingRule` rows, not versioned, A-07):

| Category | Target queue |
|---|---|
| Billing | Billing |
| Technical | Technical |
| Account | Account |

- Routing runs inside the same transaction as the ticket insert (ASM-S7). The ticket row stores `queue_id`. A TicketHistory row with event `ROUTED` and actor `system` is written.
- No endpoint accepts a client-supplied queue on create. The only path to a queue is the router.
- Admin edit: `PUT /api/admin/routing-rules/{category}` with `{target_queue_id}`. Admin only. Effective for tickets created after the change. Existing tickets are not re-routed.
- Seed teams (A-16): Billing, Technical, Account, plus `Billing Tier 2`, `Technical Tier 2`, `Account Tier 2` (used by escalation). Slugs: `billing`, `technical`, `account`, `billing-tier-2`, `technical-tier-2`, `account-tier-2`.
- Missing rule: if no rule exists for a valid category, creation fails with 409 and code `ROUTING_RULE_MISSING`. No ticket is written.

ASM-S7 (this spec): routing and ticket insert share one transaction, so a failed route leaves no ticket.

## 3. Acceptance Criteria

### AC-02 Routing assigns each new ticket to the correct team queue

- Given seed rules, When a customer creates a ticket with `category="Billing"`, Then the stored `queue_id` is the Billing queue and one TicketHistory row with event `ROUTED` exists.
- Given seed rules, When a customer creates tickets with `category="Technical"` and `category="Account"`, Then the queues are Technical and Account respectively.
- Given the seed corpus of 15 sample tickets (A-16), When the routing test runs, Then 100% of tickets sit in the queue mapped to their category (metric M2).
- Given admin calls `PUT /api/admin/routing-rules/Billing` with `target_queue_id` of Account, When a new Billing ticket is created, Then its queue is Account. The existing Billing tickets keep their queue.
- Given an agent calls `PUT /api/admin/routing-rules/Billing`, Then the response is 403 and the rule is unchanged.
- Given the Billing rule row is deleted in a test fixture, When a customer creates a Billing ticket, Then the response is 409 with code `ROUTING_RULE_MISSING` and no ticket row exists.

## 4. Architecture Constraints

- Routing rules are evaluated in `src/domain/routing` with no framework imports.
- An architecture test asserts that no API module writes `queue_id` directly (NFR-08).

## 5. Out of Scope

- ML or sentiment-based routing (BRD Section 5.2).
- Routing by priority, customer, or workload. Only category is used.
- Versioning of routing rules (A-07).
