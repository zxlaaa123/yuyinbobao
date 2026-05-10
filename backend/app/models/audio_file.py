from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from ..core.database import Base
from ..utils.time import utc_now


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    text_content = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    audio_type = Column(String(50), default="single", nullable=False, index=True)
    provider = Column(String(50), nullable=True, index=True)
    voice = Column(String(100), nullable=True)
    audio_format = Column(String(20), nullable=True, index=True)
    file_size = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
