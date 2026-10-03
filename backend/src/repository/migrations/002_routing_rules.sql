-- 002_routing_rules.sql: RoutingRule rows, not versioned (A-07, E2-S2)
CREATE TABLE routing_rules (
    category TEXT PRIMARY KEY,
    target_queue_id INTEGER NOT NULL REFERENCES teams(id)
);

INSERT INTO routing_rules (category, target_queue_id) VALUES
    ('Billing', (SELECT id FROM teams WHERE slug = 'billing')),
    ('Technical', (SELECT id FROM teams WHERE slug = 'technical')),
    ('Account', (SELECT id FROM teams WHERE slug = 'account'));
