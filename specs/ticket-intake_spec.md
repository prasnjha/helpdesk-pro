# Ticket Intake Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-01 (Sprint 1). Lifecycle and customer replies are in `ticket-lifecycle_spec.md`.
- Roles: `customer` (create, read own). Agents use other specs.

## 1. Purpose

A customer files a support ticket through the web form with title, description, category, and priority. The ticket gets an auto-generated id, starts in `OPEN`, and is routed to a team queue in the same transaction.

## 2. Behavior

- Endpoint: `POST /api/tickets`. Request: `{title, description, category, priority}`. Response 201: `{id, status, category, priority, customer_id, created_at}`.
- Ids: `HD-` plus a six-digit zero-padded sequence starting at `HD-000001` (A-12). Ids are never reused.
- Category must be one of `Billing`, `Technical`, `Account`. Priority must be one of `Critical`, `High`, `Medium`, `Low`.
- Field limits: title 1 to 200 characters; description 1 to 5000 characters (ASM-S5).
- Policy snapshot: the ticket stores the SLA policy version active for its priority at creation (ASM-S4).
- Routing runs in the same transaction as the insert (`routing_spec.md`, ASM-S7).
- Attachments (BRD A-15): accepted as `{file_name, size_bytes}` metadata only.
- Customer reads: `GET /api/tickets` lists own tickets. `GET /api/tickets/{id}` returns own tickets only. Other ids return 404. Customers never receive notes or history. Agents and admins also use `GET /api/tickets/{id}` for any ticket (`agent-workbench_spec.md`).

## 3. Acceptance Criteria

### AC-01 Customer creates a ticket in OPEN with an auto-generated id

- Given a customer C-1 with a valid bearer token, When C-1 calls `POST /api/tickets` with `title="Invoice charged twice"`, a non-empty description, `category="Billing"`, and `priority="High"`, Then the response is 201, `id` matches `^HD-\d{6}$`, `status` is `OPEN`, `customer_id` is C-1, and `created_at` is a UTC timestamp.
- Given C-1 has already created HD-000001, When C-1 creates a second ticket, Then the new id is `HD-000002`. Two creates never return the same id.
- Given no Authorization header, When `POST /api/tickets` is called, Then the response is 401 and no ticket row exists.
- Given `category="Refunds"`, When `POST /api/tickets` is called, Then the response is 422 with code `VALIDATION_ERROR` naming field `category`, and no ticket row exists.
- Given a title of 201 characters, or an empty description, When `POST /api/tickets` is called, Then the response is 422 and no ticket row exists.

## 4. Out of Scope

- Real file upload or storage (A-15).
- Notification delivery. Ticket changes are recorded as Notification rows only (A-14).
- Reopening a `RESOLVED` ticket (A-17).
- Customer visibility of other customers' tickets, even from the same company (A-04).
