# doc-writer-agent run (read-only, after fixes)

Run on branch `docs/sync-drift`, against the working tree after commits `de652b1` (doc fixes) and `863bfd6` (deposits). Read-only: no files edited, nothing installed, no tests run. Report below is the agent's own, unedited.

## Prior finding resolved?

| # | Item (prior run) | file:line (current) | Status | Evidence |
|---|---|---|---|---|
| 1 | LOG_LEVEL missing from config table | README.md:44 | RESOLVED | Row present, default INFO. backend/src/config/settings.py:31 reads LOG_LEVEL. |
| 2 | AdminUsersPage listed as existing | specs/design/component-map.md:22 | RESOLVED | Marked "Not built in this version (deferred)". No page file, no route in frontend/src/App.tsx. |
| 3 | PUT /api/admin/routing-rules/{category} | specs/design/api-contracts.md:89 | RESOLVED | Marked deferred. No route in backend/src/api. |
| 4 | POST teams, POST/PATCH users, PUT users/{id}/team | specs/design/api-contracts.md:101-104 | RESOLVED | Marked deferred. No routes. backend/src/api/app.py:34-40 includes no such router. |
| 5 | GET /api/notifications | specs/design/api-contracts.md:81, :83 | RESOLVED | Marked deferred. No notifications router. |
| 6 | Notification entity | specs/design/data-models.md:22 | RESOLVED | Marked deferred. No notifications table in migrations 001 to 009. |
| 7 | SlaEvent unique on (ticket_id, event, timer) | specs/design/data-models.md:29 | RESOLVED | Now describes the partial unique index on (ticket_id, timer) WHERE event IN breach events. Matches 007_sla_event.sql. |
| 8 | KbArticle has tags column, no created_at | specs/design/data-models.md:21 | RESOLVED | Tags in kb_article_tag. created_at listed. |
| 9 | Ticket missing timer-stop columns | specs/design/data-models.md:13 | RESOLVED | response_stopped_at and resolution_stopped_at listed (006_sla.sql). |
| 10 | User missing display_name | specs/design/data-models.md:11 | RESOLVED | display_name? listed (009_user_display_name.sql). |
| 11 | KbArticleEditor.tsx exists | specs/design/component-map.md:37 | RESOLVED (file claim) | Row now says deferred. Wording still inaccurate, see new item 11. |
| 12 | PublishToKbButton.tsx exists | specs/design/component-map.md:38 | RESOLVED (file claim) | Row now says deferred. The publish link is built inline, see new item 12. |
| 13 | Header.tsx missing from component table | specs/design/component-map.md:43 | RESOLVED | Row added. Header.tsx and Header.test.tsx exist. |
| 14 | CI sentence says frontend tests report coverage | README.md:127-130 | RESOLVED | frontend/package.json:10 is "vitest run" with no coverage flag. Sentence now matches. |

## NEW drift

| # | Doc (file:line) | Claim | Code evidence (file:line) | Proposed replacement |
|---|---|---|---|---|
| 1 | README.md:17-18 | Step 1 "Install dependencies for both services" runs `./init.sh`. | init.sh:23-24 health-checks :8000 and :5173 and exits non-zero if the servers are not up. | Step 1 becomes dependency install only. Note that init.sh health-checks both servers, so run it once both are up. |
| 2 | README.md:40-44 | Configuration table lists only DATABASE_URL, CORS_ALLOWED_ORIGINS, LOG_LEVEL. | frontend/src/api/client.ts:6 reads VITE_API_BASE_URL. frontend/playwright.config.ts reads E2E_BASE_URL. | Add both rows. |
| 3 | README.md:117 | `/agent/queues/:queue`: "Queue with priority/status/escalated filters". | QueueFilters.tsx:5-11 has queue and priority props only. | "Queue selector and priority filter." |
| 4 | README.md:49 | Demo seed gives "a knowledge base article". | seed_demo_tickets.py has no KB calls. No kb_article INSERT in migrations. | Remove the KB claim. Note the seed creates no KB article. |
| 5 | specs/design/data-models.md:19 | SlaEvent `event` lists TIMER_STARTED, RESPONSE_STOPPED, RESOLUTION_STOPPED. | Only BREACHED_RESPONSE, BREACHED_RESOLUTION (sla_repository.py:22-25, :48-51) and ESCALATED (:73-76) are written. | Mark the three other names as specified but not written. |
| 6 | specs/design/data-models.md:13 | Ticket key fields list `id` and no seq column. | 004_tickets.sql:3 `seq INTEGER PRIMARY KEY AUTOINCREMENT`. ticket_repository.py:83 derives id from seq. | Add seq as the internal PK. |
| 7 | docs/architecture.md:57 | Ticket creation inserts "TIMER_STARTED x2 events". | ticket_repository.py:92 writes only the ROUTED history row. No sla_event row at create. | Remove the TIMER_STARTED line. The spec gap is outside this check. |
| 8 | specs/design/component-map.md:31 | QueueFilters: "Priority, status, SLA state, escalated filters". | QueueFilters.tsx:5-11 has queue and priority only. | "Queue selector and priority filter." |
| 9 | specs/design/component-map.md:16 | KbArticlePage API calls: GET only. | KbArticlePage.tsx:33 sends DELETE behind a staff-only button. | Add DELETE (agent, admin). |
| 10 | specs/design/component-map.md:19 | KbEditorPage API calls include DELETE. | KbEditorPage.tsx has GET, POST and PUT only. | Replace DELETE with GET and POST and PUT. |
| 11 | specs/design/component-map.md:37 | KbArticleEditor: "Not built in this version (deferred)". | The editor form is inline in KbEditorPage.tsx (form at line 75). | "Not extracted as a component. The form is inline in KbEditorPage.tsx." |
| 12 | specs/design/component-map.md:38 | PublishToKbButton: "Not built in this version (deferred)". | AgentTicketPage.tsx:191-193 renders a publish link for RESOLVED or CLOSED tickets. | "Not extracted as a component. The link is inline in AgentTicketPage.tsx." |
| 13 | docs/architecture.md:17, :26 | Domain imports Types only, never FastAPI, SQLAlchemy or React. | pyproject.toml "Domain is pure" contract does not forbid src.config. | Add src.config to the forbidden list, or narrow the doc claim. |
| 14 | docs/architecture.md:29 | "An architecture test enforces this (NFR-08)" for queue_id. | No architecture test references queue_id. | Remove the claim, or add the test. |
| 15 | README.md:137 | "Without the key the job is skipped and the pipeline stays green." | GitLab review job is not created without the key. GitHub job runs but its steps are skipped. | Describe both behaviours. |

## Not verified

- specs/design/DESIGN.md palette, typography and Stitch references. Only mockup filenames were checked.
- specs/design/amendments/. Not read.
- README.md:62 password. Hashes not recomputed.
- Several docs/architecture.md invariants and redaction behaviour. Only test names and literal masks were checked.
- Request validation rules in api-contracts.md beyond the 405 handlers.
- Role gates for `/login` and `/kb` in README.md:116-123.

VERDICT: DRIFT FOUND (15 items)
