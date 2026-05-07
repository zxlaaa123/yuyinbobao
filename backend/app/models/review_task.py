from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..core.database import Base


class ReviewTask(Base):
    __tablename__ = "review_tasks"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    source = Column(String(20), nullable=False, default="wrong_question")
    status = Column(String(20), nullable=False, default="pending", index=True)
    difficulty = Column(String(20), nullable=False, default="medium")
    scheduled_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    snooze_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
