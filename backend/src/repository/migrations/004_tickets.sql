-- 004_tickets.sql: ticket table, HD-###### id sequence, ticket_history (E2-S1)
CREATE TABLE tickets (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    queue_id INTEGER NOT NULL REFERENCES teams(id),
    customer_id TEXT NOT NULL REFERENCES users(id),
    assignee_id TEXT REFERENCES users(id),
    escalated INTEGER NOT NULL DEFAULT 0,
    sla_policy_version_id INTEGER NOT NULL REFERENCES sla_policy(id),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX ix_tickets_queue_status_priority ON tickets (queue_id, status, priority);
CREATE INDEX ix_tickets_customer_id ON tickets (customer_id);

-- Append-only: history of status changes, routing and escalation events.
CREATE TABLE ticket_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    event TEXT NOT NULL,
    from_state TEXT,
    to_state TEXT,
    actor_id TEXT NOT NULL,
    correlation_id TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX ix_ticket_history_ticket_id ON ticket_history (ticket_id);
