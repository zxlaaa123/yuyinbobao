from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...models.wrong_question import WrongQuestion
from ...models.question import Question
from ...models.knowledge_point import KnowledgePoint

router = APIRouter(prefix="/api/wrong-questions", tags=["wrong-questions"])


@router.get("")
def list_wrong_questions(
    is_mastered: bool | None = None,
    knowledge_base_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(WrongQuestion)
    if is_mastered is not None:
        query = query.filter(WrongQuestion.is_mastered == is_mastered)

    wqs = query.order_by(WrongQuestion.last_wrong_at.desc()).all()
    q_ids = [wq.question_id for wq in wqs]
    question_query = db.query(Question).filter(Question.id.in_(q_ids)) if q_ids else None
    if question_query is not None and knowledge_base_id:
        question_query = question_query.filter(Question.knowledge_base_id == knowledge_base_id)
    q_map = {q.id: q for q in question_query.all()} if question_query is not None else {}
    kp_ids = [q.knowledge_point_id for q in q_map.values()]
    kp_map = {
        kp.id: kp
        for kp in db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()
    } if kp_ids else {}

    result = []
    for wq in wqs:
        q = q_map.get(wq.question_id)
        if not q:
            continue
        kp = kp_map.get(q.knowledge_point_id)
        result.append({
            "id": wq.id,
            "question_id": wq.question_id,
            "wrong_count": wq.wrong_count,
            "last_wrong_answer": wq.last_wrong_answer,
            "last_wrong_at": wq.last_wrong_at,
            "is_mastered": wq.is_mastered,
            "question": {
                "id": q.id,
                "question_type": q.question_type,
                "stem": q.stem,
                "options": json.loads(q.options) if q.options else [],
                "answer": q.answer,
                "analysis": q.analysis,
                "knowledge_point_title": kp.title if kp else "",
            },
        })
    return result


@router.post("/{wq_id}/mark-mastered")
def mark_mastered(wq_id: int, db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    wq.is_mastered = True
    db.commit()
    return {"id": wq.id, "is_mastered": True, "message": "已标记为掌握"}


@router.post("/{wq_id}/unmark-mastered")
def unmark_mastered(wq_id: int, db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    wq.is_mastered = False
    db.commit()
    return {"id": wq.id, "is_mastered": False, "message": "已取消掌握标记"}


@router.delete("/{wq_id}")
def delete_wrong_question(wq_id: int, db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    db.delete(wq)
    db.commit()
    return {"success": True, "message": "错题记录已删除"}
