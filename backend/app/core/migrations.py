from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_runtime_columns(engine: Engine) -> None:
    with engine.begin() as conn:
        review_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(review_tasks)")).fetchall()}
        additions = {
            "last_reviewed_at": "DATETIME",
            "last_quality": "VARCHAR(20)",
            "review_count": "INTEGER NOT NULL DEFAULT 0",
            "next_interval_days": "INTEGER NOT NULL DEFAULT 0",
        }
        for column, column_type in additions.items():
            if column not in review_columns:
                conn.execute(text(f"ALTER TABLE review_tasks ADD COLUMN {column} {column_type}"))
