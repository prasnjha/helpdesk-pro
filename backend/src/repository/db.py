"""Engine creation and the append-only migration runner (repository/CLAUDE.md)."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from sqlalchemy import Engine, create_engine, text

from src.config.settings import Settings


def make_engine(settings: Settings) -> Engine:
    is_sqlite = settings.database_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(settings.database_url, connect_args=connect_args)


def run_migrations(engine: Engine, migrations_dir: str) -> None:
    """Apply every `*.sql` file in `migrations_dir`, in filename order, exactly once.

    Migration files are never edited after they land (NFR-05); re-running this
    function is always safe because applied filenames are recorded in
    `schema_migrations`.
    """
    filenames = sorted(f for f in os.listdir(migrations_dir) if f.endswith(".sql"))
    raw = engine.raw_connection()
    try:
        cursor = raw.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "filename TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        applied = {row[0] for row in cursor.execute("SELECT filename FROM schema_migrations")}
        for filename in filenames:
            if filename in applied:
                continue
            path = os.path.join(migrations_dir, filename)
            with open(path, encoding="utf-8") as fh:
                sql = fh.read()
            cursor.executescript(sql)
            cursor.execute(
                "INSERT OR IGNORE INTO schema_migrations (filename, applied_at) VALUES (?, ?)",
                (filename, datetime.now(UTC).isoformat()),
            )
        raw.commit()
    finally:
        raw.close()


def applied_migration_count(engine: Engine) -> int:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM schema_migrations"))
        return int(result.scalar_one())
