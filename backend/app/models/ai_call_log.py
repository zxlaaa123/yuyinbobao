from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from ..core.database import Base


class AICallLog(Base):
    __tablename__ = "ai_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(80), nullable=False, index=True)
    model = Column(String(120), nullable=True, index=True)
    base_url_host = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, index=True)
    prompt_chars = Column(Integer, default=0, nullable=False)
    response_chars = Column(Integer, default=0, nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    tokens_estimated = Column(Boolean, default=False, nullable=False)
    estimated_cost = Column(Float, default=0, nullable=False)
    input_price_per_1m = Column(Float, default=0, nullable=False)
    output_price_per_1m = Column(Float, default=0, nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    request_summary = Column(Text, nullable=True)
    response_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    related_type = Column(String(50), nullable=True, index=True)
    related_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
