from sqlalchemy import Column, Integer, String, Text, DateTime
from ..core.database import Base
from ..utils.time import utc_now


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="success", nullable=False, index=True)
    trigger_type = Column(String(20), default="manual", nullable=False)
    note = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
