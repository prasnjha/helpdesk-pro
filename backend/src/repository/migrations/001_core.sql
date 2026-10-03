-- 001_core.sql: teams, users (E1-S2). The schema_migrations ledger table
-- itself is created by the migration runner before any file is applied.
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    tier INTEGER NOT NULL
);

CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    team_id INTEGER REFERENCES teams(id),
    active INTEGER NOT NULL DEFAULT 1
);

INSERT INTO teams (name, slug, tier) VALUES
    ('Billing', 'billing', 1),
    ('Technical', 'technical', 1),
    ('Account', 'account', 1),
    ('Billing Tier 2', 'billing-tier-2', 2),
    ('Technical Tier 2', 'technical-tier-2', 2),
    ('Account Tier 2', 'account-tier-2', 2);

-- Seeded demo users (synthetic data only). Password for all: Password123!
INSERT INTO users (id, username, password_hash, role, team_id, active) VALUES
    ('C-1', 'customer1', 'f2055922a06d03eb36a863cbad76837b$27f655b1c9e9d773bd576dfd51d99008c5f6ee0666cf42c77e677cfdc99cfb1f', 'customer', NULL, 1),
    ('AG-1', 'agent1', 'f14422b4ee3a62d2c01f7f23ece3894c$69e66db86c2176cb9add91a823959516fff54331434682c9c1228b670c13e169', 'agent', (SELECT id FROM teams WHERE slug = 'billing'), 1),
    ('AD-1', 'admin1', '502ee2541c73662d1f70e8f8afc8ee74$73f6c2fe2f2fb84ae4d2f338f66997536bae62d5da95c0b93eab1866db96faae', 'admin', NULL, 1);
