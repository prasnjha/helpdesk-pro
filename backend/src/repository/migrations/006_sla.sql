-- 006_sla.sql: SLA timer-stop columns (E4-S2).

ALTER TABLE tickets ADD COLUMN response_stopped_at TEXT;
ALTER TABLE tickets ADD COLUMN resolution_stopped_at TEXT;
