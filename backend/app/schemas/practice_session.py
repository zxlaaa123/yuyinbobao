from datetime import datetime
from pydantic import BaseModel, Field


class PracticeSessionItemCreate(BaseModel):
    question_id: int
    knowledge_point_id: int | None = None
    user_answer: str | None = None
    is_correct: bool
    duration_seconds: int = Field(default=0, ge=0)


class PracticeSessionCreate(BaseModel):
    mode: str = Field(default="normal", max_length=50)
    title: str | None = Field(default=None, max_length=200)
    knowledge_base_id: int | None = None
    items: list[PracticeSessionItemCreate]
    duration_seconds: int = Field(default=0, ge=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None


class PracticeSessionItemResponse(BaseModel):
    id: int
    question_id: int
    knowledge_point_id: int | None
    user_answer: str | None
    is_correct: bool
    duration_seconds: int
    question_type: str | None = None
    stem: str | None = None
    correct_answer: str | None = None
    reference_answer: str | None = None
    analysis: str | None = None
    knowledge_point_title: str | None = None
    created_at: datetime


class PracticeSessionResponse(BaseModel):
    id: int
    title: str | None
    mode: str
    knowledge_base_id: int | None
    knowledge_base_name: str | None = None
    total_count: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    duration_seconds: int
    knowledge_point_ids: list[int]
    weak_knowledge_point_ids: list[int]
    wrong_question_ids: list[int]
    suggestion: str | None
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime
    items: list[PracticeSessionItemResponse] | None = None


class PracticeSessionListResponse(BaseModel):
    items: list[PracticeSessionResponse]
    total: int
    page: int
    page_size: int
