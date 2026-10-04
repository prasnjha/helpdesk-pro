-- 008_kb.sql: knowledge base articles and tags (E5-S1, AC-09).

CREATE TABLE kb_article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    source_ticket_id TEXT NOT NULL REFERENCES tickets(id),
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX ix_kb_article_source_ticket_id ON kb_article (source_ticket_id);

CREATE TABLE kb_article_tag (
    article_id INTEGER NOT NULL REFERENCES kb_article(id),
    tag TEXT NOT NULL,
    PRIMARY KEY (article_id, tag)
);

CREATE INDEX ix_kb_article_tag_tag ON kb_article_tag (tag);
