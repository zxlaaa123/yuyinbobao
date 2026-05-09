from datetime import datetime
import sqlite3
import shutil
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.database import Base, SessionLocal, engine
from ..core.paths import BACKUP_DIR, DB_PATH
from ..models.backup_record import BackupRecord


def _backup_sqlite_file(source: Path, target: Path) -> None:
    source_conn = sqlite3.connect(str(source))
    target_conn = sqlite3.connect(str(target))
    try:
        source_conn.backup(target_conn)
    finally:
        target_conn.close()
        source_conn.close()


def _build_backup_path(prefix: str = "app") -> tuple[str, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.db"
    return filename, BACKUP_DIR / filename


def list_backups(db: Session) -> list[BackupRecord]:
    return db.query(BackupRecord).order_by(BackupRecord.id.desc()).all()


def create_backup(db: Session, note: str | None = None, trigger_type: str = "manual") -> BackupRecord:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        raise HTTPException(status_code=404, detail="数据库文件不存在，无法创建备份")

    filename, target = _build_backup_path()

    record = BackupRecord(
        filename=filename,
        file_path=str(target),
        status="pending",
        trigger_type=trigger_type,
        note=note,
        file_size=0,
    )
    db.add(record)
    db.flush()

    try:
        _backup_sqlite_file(DB_PATH, target)
        record.file_size = target.stat().st_size
        record.status = "success"
        db.commit()
        db.refresh(record)
        return record
    except Exception as exc:
        record.status = "failed"
        record.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"创建备份失败：{exc}") from exc


def restore_backup(db: Session, backup_id: int) -> dict:
    record = db.query(BackupRecord).filter(BackupRecord.id == backup_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="备份记录不存在")
    if record.status != "success":
        raise HTTPException(status_code=400, detail="只能恢复成功状态的备份")

    backup_path = Path(record.file_path)
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    safety_filename, safety_path = _build_backup_path("before_restore")

    try:
        _backup_sqlite_file(DB_PATH, safety_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"恢复前自动备份失败：{exc}") from exc

    try:
        db.close()
        engine.dispose()
        shutil.copy2(backup_path, DB_PATH)
        engine.dispose()
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"恢复备份失败：{exc}") from exc

    safety_db = SessionLocal()
    try:
        safety_record = BackupRecord(
            filename=safety_filename,
            file_path=str(safety_path),
            file_size=safety_path.stat().st_size if safety_path.exists() else 0,
            status="success",
            trigger_type="auto",
            note=f"恢复备份 {record.filename} 前自动创建",
        )
        safety_db.add(safety_record)
        safety_db.commit()
        safety_db.refresh(safety_record)
        safety_backup_id = safety_record.id
    finally:
        safety_db.close()

    return {
        "success": True,
        "message": "备份已恢复，请重启后端服务以确保连接刷新",
        "restored_backup_id": record.id,
        "safety_backup_id": safety_backup_id,
    }


def delete_backup(db: Session, backup_id: int) -> dict:
    record = db.query(BackupRecord).filter(BackupRecord.id == backup_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="备份记录不存在")

    path = Path(record.file_path)
    if path.exists():
        try:
            path.unlink()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"删除备份文件失败：{exc}") from exc

    db.delete(record)
    db.commit()
    return {"success": True, "message": "备份已删除"}
