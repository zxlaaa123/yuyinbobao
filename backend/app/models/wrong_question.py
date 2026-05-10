from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from ..core.database import Base
from ..utils.time import utc_now


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, unique=True, index=True)
    wrong_count = Column(Integer, default=1, nullable=False)
    last_wrong_answer = Column(Text, nullable=True)
    last_wrong_at = Column(DateTime, default=utc_now)
    is_mastered = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
