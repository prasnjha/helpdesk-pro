# Repository layer

- Append-only entities have insert and read methods only: ticket history, assignments, notes, replies, SLA events, SLA policy versions, notifications. No update, delete, remove or edit method. A hook blocks these.
- Ticket writes use the `version` column for optimistic concurrency and raise a conflict on a stale version.
- Routing and the ticket insert share one transaction.
- Migrations are append-only SQL files, never edited after they land.
- Entities and constraints: `specs/design/data-models.md`.