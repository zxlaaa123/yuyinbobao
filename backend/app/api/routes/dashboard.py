from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.knowledge_base import KnowledgeBase
from ...models.material import Material
from ...models.knowledge_point import KnowledgePoint
from ...models.question import Question
from ...models.wrong_question import WrongQuestion
from ...models.audio_file import AudioFile
from ...models.study_session import StudySession

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


@router.get("/recent-study-sessions")
def get_recent_study_sessions(limit: int = 5, db: Session = Depends(get_db)):
    limit = min(max(limit, 1), 20)
    sessions = db.query(StudySession).order_by(StudySession.started_at.desc()).limit(limit).all()
    kb_ids = {item.knowledge_base_id for item in sessions if item.knowledge_base_id}
    kp_ids = {item.knowledge_point_id for item in sessions if item.knowledge_point_id}
    kb_names = {
        item.id: item.name
        for item in db.query(KnowledgeBase).filter(KnowledgeBase.id.in_(kb_ids)).all()
    } if kb_ids else {}
    kp_titles = {
        item.id: item.title
        for item in db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()
    } if kp_ids else {}
    return [
        {
            "id": item.id,
            "knowledge_base_id": item.knowledge_base_id,
            "knowledge_base_name": kb_names.get(item.knowledge_base_id),
            "knowledge_point_id": item.knowledge_point_id,
            "knowledge_point_title": kp_titles.get(item.knowledge_point_id),
            "started_at": item.started_at,
            "ended_at": item.ended_at,
            "total_count": item.total_count,
            "correct_count": item.correct_count,
            "accuracy_rate": item.accuracy_rate,
        }
        for item in sessions
    ]
