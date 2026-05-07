from pydantic import BaseModel
from datetime import datetime


class MaterialCreate(BaseModel):
    knowledge_base_id: int
    title: str
    content: str
    source: str | None = None
    note: str | None = None


class MaterialUpdate(BaseModel):
    knowledge_base_id: int | None = None
    title: str | None = None
    content: str | None = None
    source: str | None = None
    note: str | None = None


class MaterialResponse(BaseModel):
    id: int
    knowledge_base_id: int
    knowledge_base_name: str = ""
    title: str
    content: str = ""
    source: str | None
    note: str | None
    material_type: str
    content_length: int
    extracted_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
