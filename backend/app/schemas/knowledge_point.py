from pydantic import BaseModel
from datetime import datetime


class KnowledgePointUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    detail: str | None = None
    exam_points: list[str] | None = None
    confusing_points: list[str] | None = None
    memory_tips: list[str] | None = None
    examples: list[str] | None = None
    importance: str | None = None
    tags: list[str] | None = None
