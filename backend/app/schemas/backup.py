from datetime import datetime
from pydantic import BaseModel


class BackupCreate(BaseModel):
    note: str | None = None


class BackupRestoreRequest(BaseModel):
    confirm: bool = False


class BackupRecordResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_size: int
    status: str
    trigger_type: str
    note: str | None = None
    error_message: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
