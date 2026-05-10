from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from .paths import AUDIO_DIR, BACKUP_DIR, DATA_DIR, DB_PATH, UPLOAD_DIR, VECTOR_STORE_DIR


def ensure_runtime_environment(engine: Engine) -> None:
    for directory in (DATA_DIR, AUDIO_DIR, UPLOAD_DIR, VECTOR_STORE_DIR, BACKUP_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        _check_writable_directory(directory)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        _check_sqlite_pragmas(conn)


def _check_writable_directory(directory: Path) -> None:
    probe = directory / ".write_test"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink(missing_ok=True)


def _check_sqlite_pragmas(conn) -> None:
    foreign_keys = conn.execute(text("PRAGMA foreign_keys")).scalar()
    busy_timeout = conn.execute(text("PRAGMA busy_timeout")).scalar()
    journal_mode = str(conn.execute(text("PRAGMA journal_mode")).scalar() or "").lower()

    if foreign_keys != 1:
        raise RuntimeError("SQLite foreign_keys 未开启")
    if journal_mode != "wal":
        raise RuntimeError("SQLite journal_mode 未开启 WAL")
    if int(busy_timeout or 0) < 30000:
        raise RuntimeError("SQLite busy_timeout 低于 30000ms")
