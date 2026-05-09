from datetime import datetime
from pydantic import BaseModel, Field


class StudySessionCreate(BaseModel):
    knowledge_base_id: int | None = None
    knowledge_point_id: int | None = None
    total_count: int = Field(default=0, ge=0)


class StudySessionFinish(BaseModel):
    total_count: int = Field(ge=0)
    correct_count: int = Field(ge=0)


class StudySessionResponse(BaseModel):
    id: int
    knowledge_base_id: int | None
    knowledge_point_id: int | None
    started_at: datetime
    ended_at: datetime | None
    total_count: int
    correct_count: int
    accuracy_rate: float

    class Config:
        from_attributes = True
