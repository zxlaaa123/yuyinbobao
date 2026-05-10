from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from ..core.database import Base
from ..utils.time import utc_now


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    mode = Column(String(50), default="normal", nullable=False, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=True, index=True)
    total_count = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    wrong_count = Column(Integer, default=0, nullable=False)
    accuracy_rate = Column(Float, default=0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    knowledge_point_ids = Column(Text, nullable=True)
    weak_knowledge_point_ids = Column(Text, nullable=True)
    wrong_question_ids = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True, index=True)
    ended_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
