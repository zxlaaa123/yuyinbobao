from pydantic import BaseModel
from datetime import datetime


class FlashcardCreate(BaseModel):
    front: str
    back: str
    flashcard_type: str = "basic"


class FlashcardUpdate(BaseModel):
    front: str | None = None
    back: str | None = None
    flashcard_type: str | None = None


class FlashcardResponse(BaseModel):
    id: int
    knowledge_point_id: int
    front: str
    back: str
    flashcard_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
