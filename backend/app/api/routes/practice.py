from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...models.question import Question
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion
from ...services.review_service import apply_answer_review_result

router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.get("/questions")
def get_practice_questions(
    knowledge_base_id: int | None = None,
    knowledge_point_id: int | None = None,
    question_type: str | None = None,
    count: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(Question)
    if knowledge_base_id:
        query = query.filter(Question.knowledge_base_id == knowledge_base_id)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    if question_type:
        query = query.filter(Question.question_type == question_type)

    questions = query.order_by(Question.id).limit(count).all()
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "question_type": q.question_type or "single_choice",
            "stem": q.stem,
            "options": json.loads(q.options) if q.options else [],
            "difficulty": q.difficulty or "medium",
            "reference_answer": q.reference_answer or q.answer,
            "knowledge_point_id": q.knowledge_point_id,
        })
    return result


@router.post("/answer")
def submit_answer(body: dict, db: Session = Depends(get_db)):
    question_id = body.get("question_id")
    user_answer = (body.get("user_answer") or "").strip()

    if not question_id:
        raise HTTPException(status_code=400, detail="缺少 question_id")
    if not user_answer:
        raise HTTPException(status_code=400, detail="请选择答案")

    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")

    is_correct = user_answer.upper() == q.answer.upper()

    # 保存答题记录
    record = AnswerRecord(
        question_id=q.id,
        user_answer=user_answer,
        is_correct=is_correct,
    )
    db.add(record)

    wrong_question_id = None
    if not is_correct:
        # 查找是否已有错题记录
        wq = db.query(WrongQuestion).filter(WrongQuestion.question_id == q.id).first()
        if wq:
            wq.wrong_count += 1
            wq.last_wrong_answer = user_answer
            wq.is_mastered = False
        else:
            wq = WrongQuestion(
                question_id=q.id,
                wrong_count=1,
                last_wrong_answer=user_answer,
                is_mastered=False,
            )
            db.add(wq)
        db.flush()
        wrong_question_id = wq.id

    review = apply_answer_review_result(db, q.knowledge_point_id, is_correct)

    db.commit()

    return {
        "question_id": q.id,
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": q.answer,
        "analysis": q.analysis or "",
        "wrong_question_id": wrong_question_id,
        "review": review,
    }
