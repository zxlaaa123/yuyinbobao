from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from ..core.database import Base
from ..utils.time import utc_now


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=True, index=True)
    started_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True, index=True)
    total_count = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    accuracy_rate = Column(Float, default=0, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
