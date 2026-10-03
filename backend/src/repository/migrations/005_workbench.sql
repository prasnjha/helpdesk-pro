-- 005_workbench.sql: assignments, ticket_notes, ticket_replies (E3-S2, E3-S3, E3-S4).
-- All three are append-only: insert and read only, no update or delete.
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    from_user_id TEXT REFERENCES users(id),
    to_user_id TEXT NOT NULL REFERENCES users(id),
    actor_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX ix_assignments_ticket_id ON assignments (ticket_id);

CREATE TABLE ticket_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    author_id TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX ix_ticket_notes_ticket_id ON ticket_notes (ticket_id);

CREATE TABLE ticket_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    author_id TEXT NOT NULL,
    author_role TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX ix_ticket_replies_ticket_id ON ticket_replies (ticket_id);

-- A second seeded agent and customer so claim/reassign/reply scenarios have
-- another active agent to hand a ticket to and another customer to isolate
-- against (synthetic seed data only). Same password for all: Password123!
INSERT INTO users (id, username, password_hash, role, team_id, active) VALUES
    ('AG-2', 'agent2', 'f14422b4ee3a62d2c01f7f23ece3894c$69e66db86c2176cb9add91a823959516fff54331434682c9c1228b670c13e169', 'agent', (SELECT id FROM teams WHERE slug = 'billing'), 1),
    ('C-2', 'customer2', 'f2055922a06d03eb36a863cbad76837b$27f655b1c9e9d773bd576dfd51d99008c5f6ee0666cf42c77e677cfdc99cfb1f', 'customer', NULL, 1);
