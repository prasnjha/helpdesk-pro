# Component Map (solo, minimal)

- Status: APPROVED

Frontend under `frontend/src/`. Each page maps to the stories it implements. Routes are gated by role; customer pages are never rendered for agents or admins, and vice versa.

## Pages

| Page (file) | Route | Roles | Stories | API calls |
|---|---|---|---|---|
| `pages/LoginPage.tsx` | `/login` | none | E2-S4 | POST `/api/auth/login` |
| `pages/MyTicketsPage.tsx` | `/tickets` | customer | E2-S4, E6-S3 | GET `/api/tickets` |
| `pages/NewTicketPage.tsx` | `/tickets/new` | customer | E2-S4 | POST `/api/tickets` |
| `pages/CustomerTicketPage.tsx` | `/tickets/:id` | customer | E3-S4, E6-S3 | GET `/api/tickets/{id}`, GET `/api/tickets/{id}/sla`, POST `/api/tickets/{id}/replies` |
| `pages/KbSearchPage.tsx` | `/kb` | customer, agent, admin | E5-S2 | GET `/api/kb/articles` |
| `pages/KbArticlePage.tsx` | `/kb/:id` | customer, agent, admin | E5-S2 | GET `/api/kb/articles/{id}` |
| `pages/WorkbenchPage.tsx` | `/agent/queues/:queue` | agent, admin | E6-S1 | GET `/api/agent/queues/{queue}/tickets` |
| `pages/AgentTicketPage.tsx` | `/agent/tickets/:id` | agent, admin | E6-S1 | GET `/api/tickets/{id}`, GET `/api/tickets/{id}/sla`, POST claim, reassign, status, notes, replies |
| `pages/KbEditorPage.tsx` | `/agent/kb/new`, `/agent/kb/:id/edit` | agent, admin | E5-S2 | POST and PUT `/api/kb/articles`, DELETE `/api/kb/articles/{id}` |
| `pages/AdminPoliciesPage.tsx` | `/admin/sla-policies` | admin | E6-S2 | GET and POST `/api/admin/sla-policies` |
| `pages/AdminDashboardPage.tsx` | `/admin/dashboard` | admin | E6-S2 | GET `/api/admin/dashboard` |
| `pages/AdminUsersPage.tsx` | `/admin/users` | admin | non-AC, seed-driven first | POST and PATCH `/api/admin/users`, PUT `/api/admin/users/{id}/team` |

## Components

| Component (file) | Used by | Purpose | Stories |
|---|---|---|---|
| `components/AuthGuard.tsx` | all protected pages | Redirects to login without a token; checks role | E2-S4 |
| `components/TicketForm.tsx` | NewTicketPage | Title, description, category, priority; client-side empty-title check, no request sent | E2-S4 |
| `components/TicketTable.tsx` | MyTicketsPage, WorkbenchPage | Rows with status, priority, SLA state badge | E2-S4, E6-S1 |
| `components/QueueFilters.tsx` | WorkbenchPage | Priority, status, SLA state, escalated filters | E6-S1 |
| `components/SlaBadge.tsx` | TicketTable, AgentTicketPage, CustomerTicketPage | Shows ON_TRACK, AT_RISK or BREACHED with minutes | E6-S1, E3-S4 |
| `components/ClaimReassignPanel.tsx` | AgentTicketPage | Claim, reassign, shows assignee without reload | E6-S1 |
| `components/StatusControl.tsx` | AgentTicketPage | Offers only the valid next states; surfaces 409 messages | E6-S1 |
| `components/ThreadPanel.tsx` | CustomerTicketPage (public replies only), AgentTicketPage (replies and notes) | Renders conversation; notes only when role is agent | E3-S3, E3-S4, E6-S1 |
| `components/ReplyBox.tsx` | CustomerTicketPage, AgentTicketPage | Body 1 to 5000 chars, posts a reply | E3-S4, E6-S1, E6-S3 |
| `components/KbArticleEditor.tsx` | KbEditorPage | Title, body, tags with validation; `source_ticket_id` read-only | E5-S2 |
| `components/PublishToKbButton.tsx` | AgentTicketPage | Visible for RESOLVED or CLOSED tickets; opens KbEditor with source id set | E5-S2, E6-S1 |
| `components/PolicyEditor.tsx` | AdminPoliciesPage | Priority, response and resolution minutes; disables edit on published versions | E6-S2 |
| `components/PolicyHistoryTable.tsx` | AdminPoliciesPage | Versions newest first | E6-S2 |
| `components/DashboardTables.tsx` | AdminDashboardPage | `open_by_queue`, `breached_by_priority`, `escalations_in_period` as tables | E6-S2 |
| `components/ErrorBanner.tsx` | all pages | Shows `error.message` from the envelope | E2-S4 |

## Shared client code

| File | Purpose |
|---|---|
| `api/client.ts` | Fetch wrapper: bearer token, parses `{error: {code, message}}` |
| `api/types.ts` | Response types matching `specs/design/api-contracts.md` |
| `state/session.ts` | Token and role in memory, with a try/catch-guarded session storage copy |

## Responsive targets

375 px (customer ticket list and reply box, no horizontal scroll), 768 px (customer and agent views), 1280 px (full agent workbench). Covered by E6-S3.
