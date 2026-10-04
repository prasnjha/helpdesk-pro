-- 007_sla_event.sql: the SlaEvent table (E4-S3).
-- sla_event is append-only: insert and read only, no update or delete.

CREATE TABLE sla_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    event TEXT NOT NULL,
    timer TEXT,
    breached_at TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX ix_sla_event_ticket_id_event ON sla_event (ticket_id, event);

-- One breach row per timer per ticket (ESCALATED has no timer and is guarded
-- in application code within the same transaction as the breach check).
CREATE UNIQUE INDEX ux_sla_event_breach_once
    ON sla_event (ticket_id, timer)
    WHERE event IN ('BREACHED_RESPONSE', 'BREACHED_RESOLUTION');
