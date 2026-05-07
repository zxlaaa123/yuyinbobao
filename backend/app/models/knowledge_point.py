from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from ..core.database import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    detail = Column(Text, nullable=True)
    exam_points = Column(Text, nullable=True)
    confusing_points = Column(Text, nullable=True)
    memory_tips = Column(Text, nullable=True)
    examples = Column(Text, nullable=True)
    importance = Column(String(20), default="medium", nullable=False, index=True)
    tags = Column(Text, nullable=True)
    ai_raw_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
