from pydantic import BaseModel
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str | None = None


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: str | None
    sort_order: int
    material_count: int = 0
    knowledge_point_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
