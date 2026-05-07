from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from ..core.database import Base


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, unique=True, index=True)
    wrong_count = Column(Integer, default=1, nullable=False)
    last_wrong_answer = Column(String(100), nullable=True)
    last_wrong_at = Column(DateTime, default=datetime.utcnow)
    is_mastered = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
