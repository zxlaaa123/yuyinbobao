from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from ..core.database import Base
from ..utils.time import utc_now


class PracticeSessionItem(Base):
    __tablename__ = "practice_session_items"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=True, index=True)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False, index=True)
    duration_seconds = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
