# Admin Console Spec

- Parent: `specs/app_spec.md`
- Status: APPROVED
- ACs: AC-10 (Sprint 3)
- Roles: `admin` only for every endpoint in this spec. Agents and customers receive 403.

## 1. Purpose

Admins change SLA commitments per priority without a code deploy. Each change creates a new immutable policy version. Admins also manage teams and agents and read a small dashboard table. Team management and the dashboard are non-AC scope (BRD 6) and may be seed-driven if time runs short.

## 2. Behavior

- `SlaPolicy` version row: `id`, `priority`, `version` (integer, starts at 1 per priority), `response_minutes`, `resolution_minutes`, `created_by`, `published_at` (UTC). Rows are append-only (NFR-05).
- Validation: `response_minutes` and `resolution_minutes` are JSON integers. Floats such as `15.5` are rejected with 422. Both must be at least 1. `resolution_minutes` must be greater than or equal to `response_minutes`.
- Seed policy values (A-10): Critical 15 and 240; High 60 and 480; Medium 240 and 1440; Low 480 and 2880.
- Endpoints:

| Method and path | Success | Notes |
|---|---|---|
| `POST /api/admin/sla-policies` `{priority, response_minutes, resolution_minutes}` | 201 | Creates the next version for that priority. It is published on creation and used for tickets created after it. |
| `GET /api/admin/sla-policies?priority=` | 200 | Returns all versions, newest first. This is the version history. |
| `PATCH` or `PUT` or `DELETE /api/admin/sla-policies/versions/{id}` | 409 | Code `POLICY_VERSION_IMMUTABLE`. No row changes. |
| `GET /api/admin/dashboard` | 200 | Counts: `open_by_queue`, `breached_by_priority`, `escalations_in_period` (query `from`, `to`). |

- Team and agent management (non-AC): `POST /api/admin/teams`, `POST /api/admin/users`, `PATCH /api/admin/users/{id}` with `{active: false}`, `PUT /api/admin/users/{id}/team`. Deactivated users cannot log in.

## 3. Acceptance Criteria

### AC-10 Admin configures SLA policy per priority without code changes; published versions immutable

- Given the seeded High policy v1 (60 and 480), When admin calls `POST /api/admin/sla-policies` with `priority="High"`, `response_minutes=45`, `resolution_minutes=360`, Then the response is 201 with `version=2`, `GET` shows v2 as the newest version for High, and v1 is unchanged.
- Given v2 is published, When a High ticket is created afterward, Then its SlaEvent targets are 45 and 360. A High ticket created before v2 keeps targets 60 and 480 (ASM-S4).
- Given published v1 for High, When admin calls `PATCH /api/admin/sla-policies/versions/{v1 id}` with `response_minutes=30`, Then the response is 409 with code `POLICY_VERSION_IMMUTABLE` and the row is unchanged. The same applies to `PUT` and `DELETE`.
- Given admin calls `POST` with `response_minutes=15.5`, Then the response is 422 and no version row is created.
- Given admin calls `POST` with `response_minutes=0`, or with `resolution_minutes=10` and `response_minutes=20`, Then the response is 422 for each, and no version row is created.
- Given agent G-1 calls `POST /api/admin/sla-policies`, Then the response is 403 and no version row is created.
- Given the static check on the admin policy module, When it runs, Then no UPDATE or DELETE statement exists for the `sla_policy` table (NFR-05).

## 4. Out of Scope

- Business-hours calendars (A-13).
- Draft or scheduled policy versions. Creation publishes immediately.
- Charts on the dashboard (A-19). A table is enough.
- Real SSO for admin login (A-08).
