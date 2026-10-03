# Sprint 4 Stories — AC-09, remaining UI, README, CI

## E5 Knowledge base

### E5-S1 KB publish and CRUD API
- Layer: API · Group: D · Depends on: E3-S1
- Description: KB article endpoints with role checks and the source-ticket rule. Covers AC-09.
- Acceptance criteria:
  1. Given an agent and a `RESOLVED` source ticket, When an article is posted, Then the response is 201 and `source_ticket_id` is fixed.
  2. Given an `OPEN` source ticket, When an article is posted, Then the response is 409 `SOURCE_TICKET_NOT_RESOLVED`.
  3. Given a customer calls `POST`, `PUT`, or `DELETE` on articles, Then the response is 403 and the article table is unchanged.

### E5-S2 KB pages
- Layer: UI · Group: D · Depends on: E5-S1
- Description: Article list with search, article detail, and an editor for agents and admins.
- Acceptance criteria:
  1. Given a customer searches `password`, Then matching article titles are listed.
  2. Given an agent saves an article with tags, Then the saved article shows those tags.
  3. Given a customer, Then no editor controls are rendered.

## E6 Console UI, docs and delivery

### E6-S1 Agent workbench UI
- Layer: UI · Group: D · Depends on: E3-S2, E3-S3, E4-S2
- Description: Queue with priority, status, and SLA-state filters, plus ticket detail with claim, reassign, status change, note, reply, and publish-to-KB.
- Acceptance criteria:
  1. Given the filter `priority=Critical`, Then only Critical tickets are listed.
  2. Given a breached ticket, Then its queue row shows the `BREACHED` state.
  3. Given a claim, Then the detail view shows the new assignee without a page reload.

### E6-S2 Admin console UI
- Layer: UI · Group: D · Depends on: E4-S1
- Description: SLA policy editor with version history, and the dashboard table (A-19). Covers the UI for AC-10.
- Acceptance criteria:
  1. Given the editor, When High is saved as 45/360, Then a new version appears first in history.
  2. Given a published version, Then its edit controls are disabled.
  3. Given the dashboard, Then `open_by_queue`, `breached_by_priority`, and `escalations_in_period` are shown as tables.

### E6-S3 Responsive layout
- Layer: UI · Group: D · Depends on: E6-S1, E5-S2, E6-S2
- Description: Layouts at 375, 768, and 1280 px (BRD 15).
- Acceptance criteria:
  1. Given a 375 px viewport, Then the customer ticket list and reply box have no horizontal page scroll.
  2. Given 768 px, Then the customer and agent views render. Given 1280 px, Then the agent workbench renders in full.
  3. Given the Playwright run, Then a snapshot exists for each breakpoint.

### E6-S4 README quick-start and seed sample tickets
- Layer: Config · Group: D · Depends on: E1-S2, E3-S4, E4-S3
- Description: README quick-start, demo credentials (A-08), and about 15 seeded tickets across states, including breach scenarios (A-16).
- Acceptance criteria:
  1. Given the README steps, Then a new developer reaches a running app with seed data in under 10 minutes (M8).
  2. Given the seed, Then tickets exist in all five lifecycle states.
  3. Given the seed, Then at least one Billing ticket is in `Billing Tier 2` after a breach.

### E6-S5 CI pipeline
- Layer: Config · Group: D · Depends on: E1-S1
- Description: CI runs backend pytest, ruff, mypy, and import-linter, frontend tests, lint, and typecheck, plus Playwright. It publishes coverage.
- Acceptance criteria:
  1. Given a failing AC-tagged test, Then the pipeline fails.
  2. Given an import-linter violation, Then the pipeline fails.
  3. Given line coverage below 80%, Then the pipeline fails (M7).

### E6-S6 Notification rows and inbox (optional stretch)
- Layer: API · Group: D · Depends on: E3-S1, E3-S3
- Description: Writes a customer Notification row on each public agent reply and on each status change, and serves `GET /api/notifications`. No delivery (A-14). No other story depends on it, so it can be dropped without blocking.
- Acceptance criteria:
  1. Given an agent public reply on a customer's ticket, Then one Notification row with kind `PUBLIC_REPLY` exists for that customer.
  2. Given a status change on a customer's ticket, Then one Notification row with kind `STATUS_CHANGED` exists for that customer.
  3. Given a user calls `GET /api/notifications`, Then only that user's rows are returned, and an internal note writes no row.
