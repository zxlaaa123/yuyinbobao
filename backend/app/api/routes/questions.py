from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...models.question import Question
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion

router = APIRouter(prefix="/api/questions", tags=["questions"])


def _to_response(q: Question) -> dict:
    reference_answer = q.reference_answer if q.reference_answer else q.answer
    return {
        "id": q.id,
        "knowledge_base_id": q.knowledge_base_id,
        "knowledge_point_id": q.knowledge_point_id,
        "question_type": q.question_type or "single_choice",
        "stem": q.stem,
        "options": json.loads(q.options) if q.options else [],
        "answer": q.answer,
        "reference_answer": reference_answer,
        "analysis": q.analysis,
        "difficulty": q.difficulty or "medium",
        "created_at": q.created_at,
        "updated_at": q.updated_at,
    }


@router.get("")
def list_questions(
    knowledge_base_id: int | None = None,
    knowledge_point_id: int | None = None,
    question_type: str | None = None,
    difficulty: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Question)
    if knowledge_base_id:
        query = query.filter(Question.knowledge_base_id == knowledge_base_id)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    if question_type:
        query = query.filter(Question.question_type == question_type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    questions = query.order_by(Question.id.desc()).all()
    return [_to_response(q) for q in questions]


@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    return _to_response(q)


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.query(AnswerRecord).filter(AnswerRecord.question_id == q.id).delete()
    db.query(WrongQuestion).filter(WrongQuestion.question_id == q.id).delete()
    db.delete(q)
    db.commit()
    return {"success": True, "message": "题目已删除"}
