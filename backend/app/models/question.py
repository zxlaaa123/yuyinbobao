from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from ..core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)
    question_type = Column(String(50), nullable=False, index=True)
    stem = Column(Text, nullable=False)
    options = Column(Text, nullable=True)
    answer = Column(String(100), nullable=False)
    analysis = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium", nullable=False, index=True)
    ai_raw_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
