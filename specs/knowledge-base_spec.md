# Knowledge Base Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-09 (Sprint 4)
- Roles: create, update, delete: `agent`, `admin`. Read and search: all authenticated roles.

## 1. Purpose

Agents turn the solution from a resolved ticket into a KB article so the next agent or customer can find it. Customers search the KB before they open a ticket (BRD 6.1). Every article is published from a source ticket, which is fixed for the article's life.

## 2. Behavior

- Entity `KbArticle`: `id`, `title` (1 to 200 chars), `body` (1 to 5000 chars), `tags` (list of 1 to 10 lowercase strings, each 1 to 30 chars), `source_ticket_id` (fixed), `created_by`, `updated_at`.
- No drafts. An article is visible as soon as it is created.
- Source ticket must be `RESOLVED` or `CLOSED`. Otherwise the request is rejected with 409 and code `SOURCE_TICKET_NOT_RESOLVED`.
- Endpoints:

| Method and path | Roles | Success |
|---|---|---|
| `POST /api/kb/articles` `{source_ticket_id, title, body, tags}` | agent, admin | 201 |
| `GET /api/kb/articles?q=&tag=` | customer, agent, admin | 200 |
| `GET /api/kb/articles/{id}` | customer, agent, admin | 200 |
| `PUT /api/kb/articles/{id}` `{title, body, tags}` | agent, admin | 200 |
| `DELETE /api/kb/articles/{id}` | agent, admin | 204 |

- `PUT` with a `source_ticket_id` in the body is rejected with 422. The field is fixed.
- Search `q` matches title and body, case-insensitive substring.

## 3. Acceptance Criteria

### AC-09 Agent publishes a resolved ticket to the KB; CRUD restricted to agent and admin

- Given agent A-1 and ticket HD-000030 in `RESOLVED`, When A-1 calls `POST /api/kb/articles` with `source_ticket_id="HD-000030"`, `title="Reset invoice portal password"`, a body, and `tags=["billing","login"]`, Then the response is 201, `source_ticket_id` is HD-000030, and the tags are stored as given.
- Given admin A-9, When A-9 calls `POST /api/kb/articles` with a `RESOLVED` source ticket, Then the response is 201.
- Given customer C-1, When C-1 calls `POST /api/kb/articles`, `PUT /api/kb/articles/{id}`, or `DELETE /api/kb/articles/{id}`, Then each response is 403 and the article table is unchanged.
- Given ticket HD-000031 in `OPEN`, When an agent calls `POST /api/kb/articles` with it as source, Then the response is 409 with code `SOURCE_TICKET_NOT_RESOLVED` and no article row exists.
- Given an existing article with source HD-000030, When an agent calls `PUT` with `source_ticket_id="HD-000031"`, Then the response is 422 and the article is unchanged.
- Given an agent calls `DELETE` on an existing article, Then the response is 204 and `GET` for that id returns 404.
- Given customer C-1 calls `GET /api/kb/articles?q=password`, Then the response is 200 and includes the HD-000030 article. Customers cannot see `source_ticket_id` pointing at another customer's ticket content; only the id is returned.

## 4. Out of Scope

- Article versioning or revision history.
- Attachments in articles.
- Ranking beyond substring match.
