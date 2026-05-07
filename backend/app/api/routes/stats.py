from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion
from ...models.audio_file import AudioFile
from ...models.knowledge_base import KnowledgeBase
from ...models.knowledge_point import KnowledgePoint
from ...models.question import Question

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    today_answers = db.query(AnswerRecord).filter(AnswerRecord.answered_at >= today).count()
    today_correct = db.query(AnswerRecord).filter(
        AnswerRecord.answered_at >= today, AnswerRecord.is_correct == True
    ).count()

    total_answers = db.query(AnswerRecord).count()
    total_correct = db.query(AnswerRecord).filter(AnswerRecord.is_correct == True).count()

    accuracy = round(total_correct / total_answers * 100, 1) if total_answers > 0 else 0

    pending_review = db.query(WrongQuestion).filter(
        WrongQuestion.is_mastered == False
    ).count()

    wrong_total = db.query(WrongQuestion).count()

    audio_success = db.query(AudioFile).filter(AudioFile.status == "success").count()
    audio_failed = db.query(AudioFile).filter(AudioFile.status == "failed").count()

    return {
        "today_answers": today_answers,
        "today_correct": today_correct,
        "total_answers": total_answers,
        "total_correct": total_correct,
        "accuracy": accuracy,
        "pending_review": pending_review,
        "wrong_total": wrong_total,
        "audio_success": audio_success,
        "audio_failed": audio_failed,
    }


@router.get("/knowledge-bases")
def get_knowledge_base_stats(db: Session = Depends(get_db)):
    kbs = db.query(KnowledgeBase).all()
    result = []
    for kb in kbs:
        kp_count = db.query(KnowledgePoint).filter(
            KnowledgePoint.knowledge_base_id == kb.id
        ).count()
        q_count = db.query(Question).filter(
            Question.knowledge_base_id == kb.id
        ).count()
        result.append({
            "id": kb.id,
            "name": kb.name,
            "knowledge_point_count": kp_count,
            "question_count": q_count,
        })
    return result
