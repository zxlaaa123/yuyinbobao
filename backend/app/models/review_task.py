from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, ForeignKey
from ..core.database import Base
from ..utils.time import utc_now


class ReviewTask(Base):
    __tablename__ = "review_tasks"
    __table_args__ = (
        CheckConstraint(
            "source in ('wrong_question', 'importance_high', 'new_knowledge')",
            name="ck_review_tasks_source",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    source = Column(String(20), nullable=False, default="wrong_question")
    status = Column(String(20), nullable=False, default="pending", index=True)
    difficulty = Column(String(20), nullable=False, default="medium")
    scheduled_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    last_reviewed_at = Column(DateTime, nullable=True)
    last_quality = Column(String(20), nullable=True)
    review_count = Column(Integer, default=0, nullable=False)
    next_interval_days = Column(Integer, default=0, nullable=False)
    snooze_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
