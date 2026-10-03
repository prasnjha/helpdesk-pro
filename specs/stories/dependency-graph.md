# Story Dependency Graph

Dependency group = sprint. Group A is Sprint 1, B is Sprint 2, C is Sprint 3, D is Sprint 4. Stories are listed in build order within each group. Every dependency points to the same group or an earlier one. No cycles.

## Group A — Sprint 1

| Order | Story | Title | Layer | Depends on |
|---|---|---|---|---|
| 1 | E1-S1 | Clock interface and error envelope | Types | — |
| 2 | E1-S4 | Seed SLA policy v1 per priority | Repository | — |
| 3 | E2-S2 | Routing rules and seed teams | Repository | — |
| 4 | E1-S2 | Seeded users and bearer-token login | Repository | E1-S1 |
| 5 | E1-S3 | Health endpoint | API | E1-S1 |
| 6 | E2-S1 | Ticket table, id sequence, create service | Repository | E1-S1, E1-S4 |
| 7 | E2-S3 | Create-ticket API with routing | API | E1-S2, E2-S1, E2-S2 |
| 8 | E2-S4 | Login page and new-ticket form | UI | E1-S2, E2-S3 |

## Group B — Sprint 2

| Order | Story | Title | Layer | Depends on |
|---|---|---|---|---|
| 1 | E3-S1 | Lifecycle state machine | Service | E2-S1 |
| 2 | E3-S2 | Claim and reassign | Service | E3-S1 |
| 3 | E3-S3 | Agent notes and public replies | API | E3-S1 |
| 4 | E3-S4 | Customer reply transition | API | E3-S1 |

## Group C — Sprint 3

| Order | Story | Title | Layer | Depends on |
|---|---|---|---|---|
| 1 | E4-S1 | SLA policy versioning API | API | E1-S4 |
| 2 | E4-S2 | Response and resolution timers | Service | E2-S1, E4-S1, E3-S1 |
| 3 | E4-S3 | Breach escalation to tier 2 | Service | E4-S2, E2-S2 |

## Group D — Sprint 4

| Order | Story | Title | Layer | Depends on |
|---|---|---|---|---|
| 1 | E6-S5 | CI pipeline | Config | E1-S1 |
| 2 | E5-S1 | KB publish and CRUD API | API | E3-S1 |
| 3 | E6-S2 | Admin console UI | UI | E4-S1 |
| 4 | E5-S2 | KB pages | UI | E5-S1 |
| 5 | E6-S1 | Agent workbench UI | UI | E3-S2, E3-S3, E4-S2 |
| 6 | E6-S3 | Responsive layout | UI | E6-S1, E5-S2, E6-S2 |
| 7 | E6-S4 | README quick-start and seed sample tickets | Config | E1-S2, E3-S4, E4-S3 |
| 8 | E6-S6 | Notification rows and inbox (optional stretch) | API | E3-S1, E3-S3 |

E6-S6 is an optional stretch story. No other story depends on it.
