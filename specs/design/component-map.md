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
| `pages/KbArticlePage.tsx` | `/kb/:id` | customer, agent, admin | E5-S2 | GET `/api/kb/articles/{id}`; DELETE `/api/kb/articles/{id}` (agent, admin, staff-only button) |
| `pages/WorkbenchPage.tsx` | `/agent/queues/:queue` | agent, admin | E6-S1 | GET `/api/agent/queues/{queue}/tickets` |
| `pages/AgentTicketPage.tsx` | `/agent/tickets/:id` | agent, admin | E6-S1 | GET `/api/tickets/{id}`, GET `/api/tickets/{id}/sla`, POST claim, reassign, status, notes, replies |
| `pages/KbEditorPage.tsx` | `/agent/kb/new`, `/agent/kb/:id/edit` | agent, admin | E5-S2 | GET `/api/kb/articles/{id}`, POST `/api/kb/articles`, PUT `/api/kb/articles/{id}` |
| `pages/AdminPoliciesPage.tsx` | `/admin/sla-policies` | admin | E6-S2 | GET and POST `/api/admin/sla-policies` |
| `pages/AdminDashboardPage.tsx` | `/admin/dashboard` | admin | E6-S2 | GET `/api/admin/dashboard` |
| `pages/AdminUsersPage.tsx` | `/admin/users` | admin | non-AC, seed-driven first | Not built in this version (deferred) |

## Components

| Component (file) | Used by | Purpose | Stories |
|---|---|---|---|
| `components/AuthGuard.tsx` | all protected pages | Redirects to login without a token; checks role | E2-S4 |
| `components/TicketForm.tsx` | NewTicketPage | Title, description, category, priority; client-side empty-title check, no request sent | E2-S4 |
| `components/TicketTable.tsx` | MyTicketsPage, WorkbenchPage | Rows with status, priority, SLA state badge | E2-S4, E6-S1 |
| `components/QueueFilters.tsx` | WorkbenchPage | Queue selector and priority filter. Status, SLA state and escalated filters are not built in this version (deferred) | E6-S1 |
| `components/SlaBadge.tsx` | TicketTable, AgentTicketPage, CustomerTicketPage | Shows ON_TRACK, AT_RISK or BREACHED with minutes | E6-S1, E3-S4 |
| `components/ClaimReassignPanel.tsx` | AgentTicketPage | Claim, reassign, shows assignee without reload | E6-S1 |
| `components/StatusControl.tsx` | AgentTicketPage | Offers only the valid next states; surfaces 409 messages | E6-S1 |
| `components/ThreadPanel.tsx` | CustomerTicketPage (public replies only), AgentTicketPage (replies and notes) | Renders conversation; notes only when role is agent | E3-S3, E3-S4, E6-S1 |
| `components/ReplyBox.tsx` | CustomerTicketPage, AgentTicketPage | Body 1 to 5000 chars, posts a reply | E3-S4, E6-S1, E6-S3 |
| `components/KbArticleEditor.tsx` | KbEditorPage | Not extracted as a component. The article form is inline in `pages/KbEditorPage.tsx` | E5-S2 |
| `components/PublishToKbButton.tsx` | AgentTicketPage | Not extracted as a component. The publish link is inline in `pages/AgentTicketPage.tsx`, shown for RESOLVED or CLOSED tickets | E5-S2, E6-S1 |
| `components/PolicyEditor.tsx` | AdminPoliciesPage | Priority, response and resolution minutes; disables edit on published versions | E6-S2 |
| `components/PolicyHistoryTable.tsx` | AdminPoliciesPage | Versions newest first | E6-S2 |
| `components/DashboardTables.tsx` | AdminDashboardPage | `open_by_queue`, `breached_by_priority`, `escalations_in_period` as tables | E6-S2 |
| `components/ErrorBanner.tsx` | all pages | Shows `error.message` from the envelope | E2-S4 |
| `components/Header.tsx` | shared layout (per-page usage not mapped) | Shared header: logo and product name | not mapped to a story |

## Shared client code

| File | Purpose |
|---|---|
| `api/client.ts` | Fetch wrapper: bearer token, parses `{error: {code, message}}` |
| `api/types.ts` | Response types matching `specs/design/api-contracts.md` |
| `state/session.ts` | Token and role in memory, with a try/catch-guarded session storage copy |

## Responsive targets

375 px (customer ticket list and reply box, no horizontal scroll), 768 px (customer and agent views), 1280 px (full agent workbench). Covered by E6-S3.

## Mockups (reference only)

Layout references from Stitch. Colours, type and spacing come from `specs/design/DESIGN.md`. If a mockup shows something this map does not list, the map wins and the extra is skipped.

| Page (file) | Mockup file |
|---|---|
| `pages/LoginPage.tsx` | `specs/design/mockups/login.png` |
| `pages/MyTicketsPage.tsx` | `specs/design/mockups/my-tickets.png` |
| `pages/NewTicketPage.tsx` | `specs/design/mockups/new-ticket.png` |
| `pages/CustomerTicketPage.tsx` | `specs/design/mockups/ticket-detail-customer-view.png` |
| `pages/KbSearchPage.tsx` | `specs/design/mockups/knowledge-base.png` |
| `pages/KbArticlePage.tsx` | `specs/design/mockups/article-detail-cisco-anyconnect-vpn.png` |
| `pages/WorkbenchPage.tsx` | `specs/design/mockups/agent-ticket-queue.png` |
| `pages/AgentTicketPage.tsx` | `specs/design/mockups/ticket-detail-active.png` (CLOSED state: `specs/design/mockups/ticket-detail-closed-variant.png`) |
| `pages/KbEditorPage.tsx` | none, follow DESIGN.md and the closest screen |
| `pages/AdminPoliciesPage.tsx` | `specs/design/mockups/admin-console.png` (shell and table style only) |
| `pages/AdminDashboardPage.tsx` | none, follow DESIGN.md and the closest screen |
| `pages/AdminUsersPage.tsx` | Not built in this version (deferred) |

The brand icon is `specs/design/mockups/helpdesk-pro-logo.png`. Use it in the header and on the login page.

### Ignore these parts of the mockups

The spec and this map win. Do not build any of the following:

- Preview-state switchers (Active Queue / Claim Conflict State / Empty State, Validation / Clean / Success, Waiting / Open / Resolved, Simulator State). These show variants only and are not UI.
- Agent Queue: Bulk Actions, Export CSV, Quick presets, a Team filter, and fixed "<30m" SLA thresholds. Use the SLA rules in the spec (AT_RISK at 80 percent of target elapsed).
- Ticket detail (agent): "Force Open" and "Force Close" buttons, "Notify requester via email and Slack", the "priority bumped to Critical" text, and the impacted-hardware panel. Escalation sets a flag and moves the queue only.
- Closed ticket: auto-closure, CSAT, audit retention and hash verification. Only "Closed tickets cannot be changed" and the locked reply box are in scope.
- New ticket: attachments, affected device, and the 15-character subject rule. The form has title, description, category and priority, with an empty-title check only.
- Customer ticket: attachments, and "Need faster turnaround".
- Knowledge Base and article: Import Markdown, Propose Changes, helpful votes, view counts, table of contents, related articles, governance panel, Print/PDF.
- Admin Console: Routing rules editor, Permissions and Roles tab, Cluster sync, and the "Access denied state" tab. Only SLA policies (list, new version, published versions read-only) is in scope.
- Login: Remember this device, SSO / Okta button.
- Pages with no mockup (KbEditorPage, AdminDashboardPage) follow DESIGN.md and the closest screen. AdminUsersPage is not built in this version (deferred).