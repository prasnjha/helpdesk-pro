# API Contracts (solo, minimal)

- Status: APPROVED

Source: `specs/app_spec.md`, feature specs, `specs/stories/`. Items marked **(assumed)** are not defined in the specs and are still open (see the end of this file).

## Common

- Base path `/api`. JSON bodies. Timestamps UTC ISO 8601. SLA values are integer minutes.
- Auth: `Authorization: Bearer <token>` on every route except `GET /health` and `POST /api/auth/login`.
- Roles: `customer`, `agent`, `admin`. Enforced in controllers (NFR-04). Admin passes every agent check; admin does not bypass the state machine.
- Error body for every 4xx and 409: `{"error": {"code": "<STABLE_CODE>", "message": "<text>"}}`. Codes are listed in `app_spec.md` Section 6.
- Cross-customer ticket reads return 404, never 403.
- Limits (ASM-S5): title 1 to 200 chars; description, reply and note body 1 to 5000 chars.
- Concurrency: every write that changes a ticket carries `version`, the value from the last read. A stale value returns 409 `VERSION_CONFLICT`.
- Queues and teams are addressed by slug: `billing`, `technical`, `account`, `billing-tier-2`, `technical-tier-2`, `account-tier-2`. Any response that shows a team includes `{slug, name}`.
- No pagination. No rate limits.

## Health and auth

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| GET `/health` | none | none | 200 `{"status": "ok"}` | none (NFR-07: 200 within 1 s of startup) |
| POST `/api/auth/login` | none | `{"username", "password"}` | 200 `{"token", "role", "username"}`. `role` and `username` were added in Sprint 4 (E6-S1/E6-S2) so the UI can route by role without a separate call. | 401 `INVALID_CREDENTIALS` (also for deactivated users) |

## Tickets (customer intake, reads and detail)

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| POST `/api/tickets` | customer | `{title, description, category, priority, attachments?: [{file_name, size_bytes}]}` | 201 `{id, status, category, priority, queue: {slug, name}, customer_id, created_at}` | 401 `UNAUTHORIZED`; 422 `VALIDATION_ERROR` (names field, e.g. `category`); 409 `ROUTING_RULE_MISSING`. No row written on any error. |
| GET `/api/tickets` | customer | none | 200 array of own tickets `{id, title, status, priority, category, updated_at}` | 401 |
| GET `/api/tickets/{id}` | customer (own only), agent, admin | none | 200 `{id, title, description, category, priority, status, queue: {slug, name}, customer_id, assignee_id, escalated, version, sla_policy_version_id, created_at, updated_at, replies, notes, history}` | 404 `NOT_FOUND` (customer, not own); 401 |

Detail view rules (decided):
- Customers receive their own public replies only. They never receive `notes` or `history`.
- Agents and admins receive all replies (public and internal), `notes`, and `history`.

## SLA read

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| GET `/api/tickets/{id}/sla` | customer (own), agent, admin | none | 200 `{"response": {target_minutes, elapsed_minutes, state, stopped_at}, "resolution": {...same...}}` | 404; 401 |

- `state` is `ON_TRACK`, `AT_RISK` or `BREACHED` (ASM-S6).
- Side effect: evaluates breach and, if a new breach is found, writes SlaEvent and escalates in one transaction (ASM-S8, escalation spec). Repeat reads write nothing new.

## Lifecycle, claim, reassign, notes, replies

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| POST `/api/tickets/{id}/claim` | agent, admin | `{version}` | 200 `{id, status, assignee_id}`. OPEN moves to IN_PROGRESS (ASM-S1). One Assignment row, `from=null` or previous. | 403 `FORBIDDEN` (customer); 404; 409 `VERSION_CONFLICT` |
| POST `/api/tickets/{id}/reassign` | agent, admin | `{assignee_id, version}` | 200 `{id, status, assignee_id}`. Status unchanged. One Assignment row. | 403; 404; 409 `VERSION_CONFLICT`; 422 `VALIDATION_ERROR` if target is not an active agent |
| POST `/api/tickets/{id}/status` | agent, admin | `{to_status, version}` | 200 `{id, status}` | 403 (customer); 404; 409 `INVALID_TICKET_STATE` (edge not in the six valid edges; no change, no history); 409 `TICKET_CLOSED_IMMUTABLE` (ticket CLOSED, logged with correlation id); 409 `VERSION_CONFLICT` |
| POST `/api/tickets/{id}/notes` | agent, admin | `{body}` | 201 `{id, ticket_id, author_id, body, created_at}` | 403 (customer); 404; 422 `VALIDATION_ERROR`; 409 `TICKET_CLOSED_IMMUTABLE` |
| POST `/api/tickets/{id}/replies` | customer (own), agent, admin | `{body}`. `author_role` set by the server from the caller's role. | 201 `{id, ticket_id, author_role, body, created_at, status}` | 404 (customer, not own); 422; 409 `INVALID_TICKET_STATE` (customer on RESOLVED or CLOSED); 409 `TICKET_CLOSED_IMMUTABLE` (agent on CLOSED) |
| PUT, PATCH, DELETE `/api/tickets/{id}/notes/{note_id}` | any | none | 405 `METHOD_NOT_ALLOWED`. No row changes. | 405 |
| PUT, PATCH, DELETE `/api/tickets/{id}/replies/{reply_id}` | any | none | 405 `METHOD_NOT_ALLOWED`. No row changes. | 405 |

Customer reply rules (lifecycle spec): on PENDING_CUSTOMER the reply and the move to OPEN commit in one transaction. On OPEN or IN_PROGRESS the status is unchanged. Both respond 201.

## Agent queues

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| GET `/api/agent/queues/{queue}/tickets` | agent, admin | `{queue}` is the team slug. Query `priority?`, `status?`, `escalated?` | 200 array `{id, title, priority, status, queue: {slug, name}, assignee_id, escalated, response_state, resolution_state}` | 403 (customer); 404 unknown slug |

## Knowledge base

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| POST `/api/kb/articles` | agent, admin | `{source_ticket_id, title, body, tags}` | 201 `{id, title, body, tags, source_ticket_id, created_by, updated_at}` | 403 (customer); 409 `SOURCE_TICKET_NOT_RESOLVED` (source not RESOLVED or CLOSED); 422 `VALIDATION_ERROR` (tags: 1 to 10 lowercase, each 1 to 30 chars) |
| GET `/api/kb/articles` | customer, agent, admin | query `q?` (case-insensitive substring over title and body), `tag?` | 200 array of article summaries | 401 |
| GET `/api/kb/articles/{id}` | customer, agent, admin | none | 200 article. Customers see `source_ticket_id` only as an id. | 404; 401 |
| PUT `/api/kb/articles/{id}` | agent, admin | `{title, body, tags}` | 200 article | 403 (customer); 404; 422 `VALIDATION_ERROR` if `source_ticket_id` is in the body (field is fixed) |
| DELETE `/api/kb/articles/{id}` | agent, admin | none | 204 | 403 (customer); 404 |

## Notifications

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| GET `/api/notifications` | customer, agent, admin | none | Not built in this version (deferred). No route, table or delivery. | n/a |

- Optional stretch story E6-S6. Deferred: no notifications router, no migration, no delivery and no mark-as-read.

## Admin: routing and SLA policy

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| PUT `/api/admin/routing-rules/{category}` | admin | `{target_queue_id}` | Not built in this version (deferred). Routing rules are seed data only. | n/a |
| POST `/api/admin/sla-policies` | admin | `{priority, response_minutes, resolution_minutes}` | 201 `{id, priority, version, response_minutes, resolution_minutes, published_at}` | 403; 422 `VALIDATION_ERROR` (float, value below 1, or resolution below response) |
| GET `/api/admin/sla-policies` | admin | query `priority?` | 200 array of all versions, newest first | 403 |
| PATCH, PUT, DELETE `/api/admin/sla-policies/versions/{id}` | admin | none | 409 `POLICY_VERSION_IMMUTABLE`. No row changes. | 409; 403 (non-admin) |
| GET `/api/admin/dashboard` | admin | query `from`, `to` | 200 `{open_by_queue: [{queue: {slug, name}, count}], breached_by_priority: [{priority, count}], escalations_in_period: int}` | 403; 422 bad date range |

## Admin: teams and users (non-AC, may be seed-driven)

Not built in this version (deferred). Teams and users are seed data only. The rows below are the planned contract.

| Method and path | Roles | Request | Success | Errors |
|---|---|---|---|---|
| POST `/api/admin/teams` | admin | `{name}` | Not built in this version (deferred) | n/a |
| POST `/api/admin/users` | admin | `{username, role, team_id?}` | Not built in this version (deferred) | n/a |
| PATCH `/api/admin/users/{id}` | admin | `{active: false}` | Not built in this version (deferred) | n/a |
| PUT `/api/admin/users/{id}/team` | admin | `{team_id}` | Not built in this version (deferred) | n/a |

## Still open

None. The `(assumed)` markers left in this file are names the team has accepted, except the notification `kind` names, which are still assumed.
