from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from ..core.database import Base
from ..utils.time import utc_now


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
    mastery_level = Column(Integer, default=0, nullable=False)
    review_count = Column(Integer, default=0, nullable=False)
    correct_streak = Column(Integer, default=0, nullable=False)
    wrong_streak = Column(Integer, default=0, nullable=False)
    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, default=utc_now, nullable=True, index=True)
    review_status = Column(String(20), default="new", nullable=False, index=True)
    ai_raw_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
