from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from ..core.database import Base
from ..utils.time import utc_now


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(300), nullable=True)
    note = Column(Text, nullable=True)
    material_type = Column(String(50), default="text", nullable=False)
    file_path = Column(String(500), nullable=True)
    content_length = Column(Integer, default=0)
    extracted_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
