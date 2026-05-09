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

        ai_log_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(ai_call_logs)")).fetchall()}
        ai_log_additions = {
            "tokens_estimated": "BOOLEAN NOT NULL DEFAULT 0",
            "input_price_per_1m": "FLOAT NOT NULL DEFAULT 0",
            "output_price_per_1m": "FLOAT NOT NULL DEFAULT 0",
        }
        for column, column_type in ai_log_additions.items():
            if ai_log_columns and column not in ai_log_columns:
                conn.execute(text(f"ALTER TABLE ai_call_logs ADD COLUMN {column} {column_type}"))

        audio_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(audio_files)")).fetchall()}
        audio_additions = {
            "audio_type": "VARCHAR(50) NOT NULL DEFAULT 'single'",
            "provider": "VARCHAR(50)",
            "voice": "VARCHAR(100)",
            "audio_format": "VARCHAR(20)",
            "file_size": "INTEGER",
        }
        for column, column_type in audio_additions.items():
            if audio_columns and column not in audio_columns:
                conn.execute(text(f"ALTER TABLE audio_files ADD COLUMN {column} {column_type}"))
        if audio_columns:
            conn.execute(text("UPDATE audio_files SET audio_type = 'collection' WHERE audio_type = 'single' AND title LIKE '合集%'"))
            conn.execute(text("UPDATE audio_files SET audio_type = 'daily_review' WHERE audio_type = 'single' AND title LIKE '每日复习%'"))
            conn.execute(text("UPDATE audio_files SET audio_type = 'wrong_question' WHERE audio_type = 'single' AND title LIKE '错题复习%'"))
