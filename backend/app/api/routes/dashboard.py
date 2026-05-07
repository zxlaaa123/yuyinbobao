from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.knowledge_base import KnowledgeBase
from ...models.material import Material
from ...models.knowledge_point import KnowledgePoint
from ...models.question import Question
from ...models.wrong_question import WrongQuestion
from ...models.audio_file import AudioFile

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return {
        "knowledge_base_count": db.query(KnowledgeBase).count(),
        "material_count": db.query(Material).count(),
        "knowledge_point_count": db.query(KnowledgePoint).count(),
        "question_count": db.query(Question).count(),
        "wrong_question_count": db.query(WrongQuestion).count(),
        "audio_count": db.query(AudioFile).filter(AudioFile.status == "success").count(),
    }
