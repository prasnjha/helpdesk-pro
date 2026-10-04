# doc-writer-agent run (read-only)

Run once against the repo at this commit, by a general-purpose agent following `.claude/agents/doc-writer-agent.md`. No files were edited, and no installs or tests were run. The proposed replacements below are not applied.

## Drift table

Rows are grouped by check. Code evidence paths are relative to the repo root.

### Check 2: Env vars and config

| Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|
| README.md:40-43 | Configuration table lists only DATABASE_URL and CORS_ALLOWED_ORIGINS. LOG_LEVEL is missing. | backend/src/config/settings.py:31 reads `LOG_LEVEL`, default `INFO`. docs/architecture.md:92 documents it. | Add row: `| \`LOG_LEVEL\` | \`INFO\` | Log level for the JSON log lines (DEBUG, INFO, WARNING, ERROR) |` |

### Check 3: Routes and pages

| Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|
| specs/design/component-map.md:22 | `/admin/users` page (`pages/AdminUsersPage.tsx`) exists. | No `AdminUsersPage.tsx` in frontend/src. No `/admin/users` route in frontend/src/App.tsx:19-106. | Replace the row with "not in this build (no route, no page)", or delete it. |

### Check 4: API contracts

| Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|
| specs/design/api-contracts.md:90 | `PUT /api/admin/routing-rules/{category}` exists. | No route. backend/src/api/routers/admin.py covers only `/api/admin/sla-policies` and `/api/admin/dashboard`. `routing_rules` is read in backend/src/repository/routing_repository.py:9 only. | Add "Not implemented in this build" to the Success column, or remove the row. |
| specs/design/api-contracts.md:100-103 | `POST /api/admin/teams`, `POST /api/admin/users`, `PATCH /api/admin/users/{id}`, `PUT /api/admin/users/{id}/team` exist. | No routes found. | Mark the section "Not implemented in this build; seed data only." |
| specs/design/api-contracts.md:81 (section 77-84) | `GET /api/notifications` exists. | No route and no notifications router. | Replace the section body with "Not implemented in this build. No route, table or delivery." |

Checked and in sync: every other contract endpoint has a matching method and path in backend/src/api/routers. Roles match the require_role or get_current_user checks. All error codes in the contract exist in backend/src/types/errors.py. The `username` field in the login response was not confirmed.

### Check 5: Data models

| Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|
| specs/design/data-models.md:22 | `Notification` entity. | No CREATE TABLE for notifications in migrations 001 to 009. | Mark "Not implemented in this build (no migration)", or delete the row. |
| specs/design/data-models.md:29 | SlaEvent unique on `(ticket_id, event, timer)` for breach events. | backend/src/repository/migrations/007_sla_event.sql:14-16 defines a partial unique index on `(ticket_id, timer)` WHERE event IN ('BREACHED_RESPONSE','BREACHED_RESOLUTION'). | Describe the partial unique index as in the migration. ESCALATED is guarded in application code. |
| specs/design/data-models.md:21 | KbArticle has a `tags` column and no `created_at`. | backend/src/repository/migrations/008_kb.sql:3-15: tags live in `kb_article_tag(article_id, tag)`, and `created_at` exists. | Replace the tags field with a reference to `kb_article_tag`. Add `created_at`. |
| specs/design/data-models.md:13 | Ticket key fields omit two columns. | backend/src/repository/migrations/006_sla.sql:3-4 adds `response_stopped_at` and `resolution_stopped_at`. | Append both as nullable UTC fields. |
| specs/design/data-models.md:11 | User key fields omit display_name. | backend/src/repository/migrations/009_user_display_name.sql:2. | Append `display_name?`. |

Checked and in sync: the Team, TicketHistory, Assignment, TicketNote, TicketReply, SlaPolicy and RoutingRule tables and their key columns. The listed indexes exist. Enum values match the code tables and constraints.

### Check 6: Component map

| Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|
| specs/design/component-map.md:37 | `components/KbArticleEditor.tsx` exists. | No such file in frontend/src. | Delete the row, or point it at the file that holds the editor form (not verified). |
| specs/design/component-map.md:38 | `components/PublishToKbButton.tsx` exists. | No such file. The publish link may be inline in `pages/AgentTicketPage.tsx` (not verified). | Delete the row, or point it at the file that holds the link. |
| specs/design/component-map.md:24-42 | The components table does not list Header. | frontend/src/components/Header.tsx exists, with a test file. | Add a Header row. |

Checked and in sync: all other page and component files in the map exist. All 11 mockup paths exist. The responsive targets match frontend/playwright.config.ts and frontend/e2e/responsive.spec.ts.

### Check 7: Paths and layer rules

No drift found. The file references in docs/architecture.md resolve. Observation only: the layers contract in backend/pyproject.toml omits src.domain, so the Domain position in the diagram is enforced only by the "Domain is pure" forbidden contract.

### Check 8: Counts and claims

| Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|
| README.md:126-127 | CI runs "tests with coverage for both backend and frontend". | Frontend test script is `vitest run` with no coverage flag (frontend/package.json:10). Only the backend produces coverage.xml. | "Backend tests report coverage (`backend/coverage.xml`, floor 80%). Frontend unit tests produce no coverage report." |

Checked and in sync: the seed user count (5), the seeded teams (6), the "about 15 demo tickets" claim, the 80% coverage floor, and the Billing Tier 2 demo claim.

### Check 1: Commands (in sync)

Every README command resolves to a real script or entry point.

### Also in sync

- README Quick start and the /health check.
- README defaults for DATABASE_URL and CORS.
- README Pages table: all 11 routes exist in frontend/src/App.tsx with matching role gates.
- README CI description for GitLab and GitHub.
- architecture.md layer diagram matches the layers contract.

### Not verified

- specs/design/DESIGN.md: palette, typography and Stitch project reference. Only mockup paths were checked.
- docs/architecture.md redaction rules and stop-list behaviour in log_redaction.py. Module names only were confirmed.
- Invariant claims in architecture.md ("checked by tests").
- The `username` field in the login response.

## VERDICT: DRIFT FOUND (14 items)
