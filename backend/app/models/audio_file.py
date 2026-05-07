from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from ..core.database import Base


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    text_content = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
