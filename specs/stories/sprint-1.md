# Sprint 1 Stories — AC-01, AC-02 and enablers

Acceptance: AC-01, AC-02. Enablers: login, Clock, health, SLA seed, routing seed, minimal UI.

## E1 Platform foundation

### E1-S1 Clock interface and error envelope
- Layer: Types · Group: A · Depends on: none
- Description: Adds the injectable Clock (A-20) and the error body `{"error": {"code", "message"}}` (app_spec §6). All later code reads time and errors through these.
- Acceptance criteria:
  1. Given a test Clock, When it is advanced 15 minutes, Then `now()` is exactly 15 minutes later and no sleep occurs.
  2. Given any 4xx or 409 response, Then the body has exactly `error.code` and `error.message`.
  3. Given the Clock module, When the static check runs, Then it contains no float type or float literal (NFR-01).

### E1-S2 Seeded users and bearer-token login
- Layer: Repository · Group: A · Depends on: E1-S1
- Description: Seeded customer, agent, and admin accounts with hashed passwords, plus `POST /api/auth/login` returning a bearer token (A-08). Demo credentials are documented in the README (E6-S4).
- Acceptance criteria:
  1. Given seeded customer C-1 and the correct password, When `POST /api/auth/login` is called, Then the response is 200 with a bearer token.
  2. Given a wrong password, When login is called, Then the response is 401 with code `INVALID_CREDENTIALS` and no token.
  3. Given no token, When a protected route is called, Then the response is 401.

### E1-S3 Health endpoint
- Layer: API · Group: A · Depends on: E1-S1
- Description: `GET /health` as the readiness check (NFR-07). It needs no token.
- Acceptance criteria:
  1. Given the app has started, When `GET /health` is called within 1 second of startup, Then the response is 200.
  2. Given the app is running, When `GET /health` is called without a token, Then the response is 200.
  3. Given a 200 response, Then the JSON body has `status` equal to `ok`.

### E1-S4 Seed SLA policy v1 per priority
- Layer: Repository · Group: A · Depends on: none
- Description: Migration creates the `sla_policy` table and inserts version 1 for each priority with the A-10 values. Tickets can then snapshot a policy version from their first request (ASM-S4). Migrations are append-only (NFR-05).
- Acceptance criteria:
  1. Given a fresh database after migrations, Then exactly four v1 rows exist, one per priority.
  2. Given the seed, Then Critical is 15/240, High 60/480, Medium 240/1440, and Low 480/2880 (response/resolution minutes).
  3. Given the migration is applied twice, Then the migration ledger prevents re-application and the row count stays 4.

## E2 Ticket intake and routing

### E2-S1 Ticket table, id sequence, create service
- Layer: Repository · Group: A · Depends on: E1-S1, E1-S4
- Description: Ticket table with the BRD §9 fields, the `HD-` id sequence (A-12), and a create service that stores the active policy version id (ASM-S4). Routing is added in E2-S3 before any API exposes creation.
- Acceptance criteria:
  1. Given two sequential creates, Then the ids are `HD-000001` and `HD-000002`, and no id is reused.
  2. Given a create for priority High, Then the row stores the id of the active High policy version.
  3. Given an insert fails, Then no partial ticket row remains.

### E2-S2 Routing rules and seed teams
- Layer: Repository · Group: A · Depends on: none
- Description: `RoutingRule` rows mapping Billing, Technical, and Account to their teams, plus six seed teams including the three tier-2 queues (A-06, A-16). Rules are plain rows, not versioned (A-07).
- Acceptance criteria:
  1. Given seed data, Then each category has exactly one rule pointing to the team of the same name.
  2. Given seed data, Then `Billing Tier 2`, `Technical Tier 2`, and `Account Tier 2` exist as teams.
  3. Given a routing rule is changed, Then existing tickets keep their queue (`routing_spec.md` §2).

### E2-S3 Create-ticket API with routing
- Layer: API · Group: A · Depends on: E1-S2, E2-S1, E2-S2
- Description: `POST /api/tickets` validates input, routes, and inserts in one transaction (ASM-S7), then writes the ROUTED history row. Covers AC-01 and AC-02.
- Acceptance criteria:
  1. Given a valid Billing request with a token, Then the response is 201 with status `OPEN` and queue Billing.
  2. Given category `Refunds`, Then the response is 422 with code `VALIDATION_ERROR` and no row is written.
  3. Given no rule for the category, Then the response is 409 with code `ROUTING_RULE_MISSING` and no row is written.

### E2-S4 Login page and new-ticket form
- Layer: UI · Group: A · Depends on: E1-S2, E2-S3
- Description: Minimal React sign-in page and new-ticket form, enough for Playwright to drive AC-01 and AC-02. Visual polish is out of scope (BRD 15).
- Acceptance criteria:
  1. Given seeded credentials, When a user signs in, Then the app stores the token and shows the ticket list.
  2. Given a valid form, When submitted, Then the confirmation shows the `HD-` id and status `OPEN`.
  3. Given an empty title, Then the form shows a validation message and sends no request.
