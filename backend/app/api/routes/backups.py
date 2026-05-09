from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.backup import BackupCreate, BackupRecordResponse, BackupRestoreRequest
from ...services.backup_service import create_backup, delete_backup, list_backups, restore_backup

router = APIRouter(prefix="/api/backups", tags=["backups"])


@router.get("", response_model=list[BackupRecordResponse])
def get_backups(db: Session = Depends(get_db)):
    return list_backups(db)


@router.post("", response_model=BackupRecordResponse)
def post_backup(body: BackupCreate | None = None, db: Session = Depends(get_db)):
    return create_backup(db, note=body.note if body else None)


@router.post("/{backup_id}/restore")
def post_restore_backup(backup_id: int, body: BackupRestoreRequest, db: Session = Depends(get_db)):
    if not body.confirm:
        raise HTTPException(status_code=400, detail="恢复备份前必须二次确认")
    return restore_backup(db, backup_id)


@router.delete("/{backup_id}")
def delete_backup_record(backup_id: int, db: Session = Depends(get_db)):
    return delete_backup(db, backup_id)
