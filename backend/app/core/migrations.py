from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_runtime_columns(engine: Engine) -> None:
    with engine.begin() as conn:
        question_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(questions)")).fetchall()}
        question_additions = {
            "question_type": "VARCHAR(50) NOT NULL DEFAULT 'single_choice'",
            "difficulty": "VARCHAR(20) NOT NULL DEFAULT 'medium'",
            "reference_answer": "TEXT",
        }
        for column, column_type in question_additions.items():
            if question_columns and column not in question_columns:
                conn.execute(text(f"ALTER TABLE questions ADD COLUMN {column} {column_type}"))
        if question_columns:
            conn.execute(text("UPDATE questions SET question_type = 'single_choice' WHERE question_type IS NULL OR question_type = ''"))
            conn.execute(text("UPDATE questions SET difficulty = 'medium' WHERE difficulty IS NULL OR difficulty = ''"))

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

        kp_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(knowledge_points)")).fetchall()}
        kp_additions = {
            "mastery_level": "INTEGER NOT NULL DEFAULT 0",
            "review_count": "INTEGER NOT NULL DEFAULT 0",
            "correct_streak": "INTEGER NOT NULL DEFAULT 0",
            "wrong_streak": "INTEGER NOT NULL DEFAULT 0",
            "last_reviewed_at": "DATETIME",
            "next_review_at": "DATETIME",
            "review_status": "VARCHAR(20) NOT NULL DEFAULT 'new'",
        }
        for column, column_type in kp_additions.items():
            if kp_columns and column not in kp_columns:
                conn.execute(text(f"ALTER TABLE knowledge_points ADD COLUMN {column} {column_type}"))
        if kp_columns:
            conn.execute(text("UPDATE knowledge_points SET review_status = 'new' WHERE review_status IS NULL OR review_status = ''"))
            conn.execute(text("UPDATE knowledge_points SET mastery_level = 0 WHERE mastery_level IS NULL"))
            conn.execute(text("UPDATE knowledge_points SET review_count = 0 WHERE review_count IS NULL"))
            conn.execute(text("UPDATE knowledge_points SET correct_streak = 0 WHERE correct_streak IS NULL"))
            conn.execute(text("UPDATE knowledge_points SET wrong_streak = 0 WHERE wrong_streak IS NULL"))
            conn.execute(text("UPDATE knowledge_points SET next_review_at = created_at WHERE next_review_at IS NULL"))

        ai_log_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(ai_call_logs)")).fetchall()}
        ai_log_additions = {
            "tokens_estimated": "BOOLEAN NOT NULL DEFAULT 0",
            "input_price_per_1m": "FLOAT NOT NULL DEFAULT 0",
            "output_price_per_1m": "FLOAT NOT NULL DEFAULT 0",
            "error_type": "VARCHAR(50)",
            "json_parse_status": "VARCHAR(30) NOT NULL DEFAULT 'not_required'",
            "http_status_code": "INTEGER",
        }
        for column, column_type in ai_log_additions.items():
            if ai_log_columns and column not in ai_log_columns:
                conn.execute(text(f"ALTER TABLE ai_call_logs ADD COLUMN {column} {column_type}"))

        session_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(study_sessions)")).fetchall()}
        session_additions = {
            "updated_at": "DATETIME",
        }
        for column, column_type in session_additions.items():
            if session_columns and column not in session_columns:
                conn.execute(text(f"ALTER TABLE study_sessions ADD COLUMN {column} {column_type}"))

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
