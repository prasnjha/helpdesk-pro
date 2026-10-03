-- 003_sla_policy.sql: SlaPolicy v1 seed per priority (E1-S4, A-10). Append-only, never UPDATE/DELETE.
CREATE TABLE sla_policy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    priority TEXT NOT NULL,
    version INTEGER NOT NULL,
    response_minutes INTEGER NOT NULL,
    resolution_minutes INTEGER NOT NULL,
    created_by TEXT NOT NULL,
    published_at TEXT NOT NULL,
    UNIQUE (priority, version)
);

INSERT INTO sla_policy (priority, version, response_minutes, resolution_minutes, created_by, published_at) VALUES
    ('Critical', 1, 15, 240, 'system', '2026-01-01T00:00:00Z'),
    ('High', 1, 60, 480, 'system', '2026-01-01T00:00:00Z'),
    ('Medium', 1, 240, 1440, 'system', '2026-01-01T00:00:00Z'),
    ('Low', 1, 480, 2880, 'system', '2026-01-01T00:00:00Z');
