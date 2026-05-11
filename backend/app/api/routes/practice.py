from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import re
from ...core.database import get_db
from ...models.question import Question
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion
from ...services.review_service import apply_answer_review_result

router = APIRouter(prefix="/api/practice", tags=["practice"])


def _normalize_text_answer(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _answer_to_text(value) -> str:
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value or "")


def _normalize_multi_answer(value) -> str:
    raw = _answer_to_text(value).strip().upper()
    parts = [part for part in re.split(r"[\s,;，；、]+", raw) if part]
    return ",".join(sorted(set(parts)))


def _load_options(value: str | None) -> list:
    if not value:
        return []
    try:
        options = json.loads(value)
        return options if isinstance(options, list) else []
    except Exception:
        return []


def _validate_answer(question: Question, user_answer) -> str:
    question_type = question.question_type or "single_choice"
    answer_text = _answer_to_text(user_answer).strip()
    if not answer_text:
        raise HTTPException(status_code=400, detail="请选择答案")

    if question_type == "multiple_choice":
        normalized = _normalize_multi_answer(user_answer)
        if not normalized:
            raise HTTPException(status_code=400, detail="请选择答案")
        valid_labels = {
            str(option.get("label", "")).strip().upper()
            for option in _load_options(question.options)
            if isinstance(option, dict) and option.get("label")
        }
        selected = set(normalized.split(","))
        if valid_labels and not selected.issubset(valid_labels):
            raise HTTPException(status_code=400, detail="选项不在题目范围内")
        return normalized

    return answer_text


def _is_answer_correct(question: Question, user_answer) -> bool:
    question_type = question.question_type or "single_choice"
    correct_answer = question.answer or ""
    if question_type == "multiple_choice":
        return _normalize_multi_answer(user_answer) == _normalize_multi_answer(correct_answer)
    if question_type == "true_false":
        correct = _normalize_text_answer(correct_answer)
        user = _normalize_text_answer(_answer_to_text(user_answer))
        true_values = {"正确", "对", "是", "true", "a", "1", "yes"}
        false_values = {"错误", "错", "否", "false", "b", "0", "no"}
        correct_is_true = correct in true_values
        correct_is_false = correct in false_values
        user_is_true = user in true_values
        user_is_false = user in false_values
        if correct_is_true:
            return user_is_true
        if correct_is_false:
            return user_is_false
        return user == correct
    if question_type in {"fill_blank", "short_answer"}:
        return _normalize_text_answer(user_answer) == _normalize_text_answer(correct_answer)
    return _normalize_text_answer(user_answer) == _normalize_text_answer(correct_answer)


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
    user_answer_raw = body.get("user_answer")

    if not question_id:
        raise HTTPException(status_code=400, detail="缺少 question_id")
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")

    user_answer = _validate_answer(q, user_answer_raw)
    is_correct = _is_answer_correct(q, user_answer)

    try:
        record = AnswerRecord(
            question_id=q.id,
            user_answer=user_answer,
            is_correct=is_correct,
        )
        db.add(record)

        wrong_question_id = None
        if not is_correct:
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
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="提交答案失败，请稍后重试") from exc

    return {
        "question_id": q.id,
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": q.answer,
        "reference_answer": q.reference_answer or q.answer,
        "analysis": q.analysis or "",
        "wrong_question_id": wrong_question_id,
        "review": review,
    }
