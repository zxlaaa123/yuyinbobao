from collections import Counter
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.knowledge_base import KnowledgeBase
from ...models.knowledge_point import KnowledgePoint
from ...models.practice_session import PracticeSession
from ...models.practice_session_item import PracticeSessionItem
from ...models.question import Question
from ...schemas.practice_session import (
    PracticeSessionCreate,
    PracticeSessionItemResponse,
    PracticeSessionListResponse,
    PracticeSessionResponse,
)
from ...utils.time import utc_now

router = APIRouter(prefix="/api/practice/sessions", tags=["practice-sessions"])


def _dump_int_list(values: list[int]) -> str:
    uniq = sorted({int(v) for v in values if isinstance(v, int)})
    return json.dumps(uniq, ensure_ascii=False)


def _load_int_list(value: str | None) -> list[int]:
    if not value:
        return []
    try:
        raw = json.loads(value)
        if isinstance(raw, list):
            return [int(v) for v in raw if isinstance(v, int)]
    except Exception:
        return []
    return []


def _build_session_response(
    db: Session,
    session: PracticeSession,
    *,
    include_items: bool,
    knowledge_base_name: str | None = None,
) -> PracticeSessionResponse:
    kb_name = knowledge_base_name
    if kb_name is None and session.knowledge_base_id:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == session.knowledge_base_id).first()
        kb_name = kb.name if kb else None

    response_items = None
    if include_items:
        items = db.query(PracticeSessionItem).filter(PracticeSessionItem.session_id == session.id).order_by(PracticeSessionItem.id.asc()).all()
        q_ids = [it.question_id for it in items]
        kp_ids = [it.knowledge_point_id for it in items if it.knowledge_point_id]
        q_map = {q.id: q for q in db.query(Question).filter(Question.id.in_(q_ids)).all()} if q_ids else {}
        kp_map = {kp.id: kp.title for kp in db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()} if kp_ids else {}
        response_items = [
            PracticeSessionItemResponse(
                id=it.id,
                question_id=it.question_id,
                knowledge_point_id=it.knowledge_point_id,
                user_answer=it.user_answer,
                is_correct=it.is_correct,
                duration_seconds=it.duration_seconds,
                question_type=(q_map.get(it.question_id).question_type if q_map.get(it.question_id) else None),
                stem=(q_map.get(it.question_id).stem if q_map.get(it.question_id) else None),
                correct_answer=(q_map.get(it.question_id).answer if q_map.get(it.question_id) else None),
                reference_answer=(q_map.get(it.question_id).reference_answer if q_map.get(it.question_id) else None),
                analysis=(q_map.get(it.question_id).analysis if q_map.get(it.question_id) else None),
                knowledge_point_title=kp_map.get(it.knowledge_point_id) if it.knowledge_point_id else None,
                created_at=it.created_at,
            )
            for it in items
        ]

    return PracticeSessionResponse(
        id=session.id,
        title=session.title,
        mode=session.mode,
        knowledge_base_id=session.knowledge_base_id,
        knowledge_base_name=kb_name,
        total_count=session.total_count,
        correct_count=session.correct_count,
        wrong_count=session.wrong_count,
        accuracy_rate=session.accuracy_rate,
        duration_seconds=session.duration_seconds,
        knowledge_point_ids=_load_int_list(session.knowledge_point_ids),
        weak_knowledge_point_ids=_load_int_list(session.weak_knowledge_point_ids),
        wrong_question_ids=_load_int_list(session.wrong_question_ids),
        suggestion=session.suggestion,
        started_at=session.started_at,
        ended_at=session.ended_at,
        created_at=session.created_at,
        items=response_items,
    )


@router.post("", response_model=PracticeSessionResponse)
def create_practice_session(body: PracticeSessionCreate, db: Session = Depends(get_db)):
    if not body.items:
        raise HTTPException(status_code=400, detail="items 不能为空")

    if body.knowledge_base_id:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == body.knowledge_base_id).first()
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")

    question_ids = [item.question_id for item in body.items]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    q_map = {q.id: q for q in questions}
    missing = [qid for qid in question_ids if qid not in q_map]
    if missing:
        raise HTTPException(status_code=400, detail=f"题目不存在：{missing[0]}")

    kp_ids: list[int] = []
    wrong_q_ids: list[int] = []
    kp_wrong_counter: Counter[int] = Counter()
    correct_count = 0

    for item in body.items:
        kp_id = item.knowledge_point_id or q_map[item.question_id].knowledge_point_id
        if item.is_correct:
            correct_count += 1
        else:
            wrong_q_ids.append(item.question_id)
            if kp_id:
                kp_wrong_counter[kp_id] += 1

        if kp_id:
            kp_ids.append(kp_id)

    total_count = len(body.items)
    wrong_count = total_count - correct_count
    accuracy_rate = round(correct_count / total_count * 100, 1) if total_count else 0

    weak_kp_ids = [kp_id for kp_id, cnt in kp_wrong_counter.items() if cnt > 0]
    suggestion = None
    if weak_kp_ids:
        kp_titles = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(weak_kp_ids)).all()
        weak_titles = "、".join([kp.title for kp in kp_titles][:3])
        suggestion = f"建议优先复习：{weak_titles}" if weak_titles else "建议优先复习本次错误较多的知识点。"

    try:
        session = PracticeSession(
            title=body.title,
            mode=body.mode or "normal",
            knowledge_base_id=body.knowledge_base_id,
            total_count=total_count,
            correct_count=correct_count,
            wrong_count=wrong_count,
            accuracy_rate=accuracy_rate,
            duration_seconds=body.duration_seconds,
            knowledge_point_ids=_dump_int_list(kp_ids),
            weak_knowledge_point_ids=_dump_int_list(weak_kp_ids),
            wrong_question_ids=_dump_int_list(wrong_q_ids),
            suggestion=suggestion,
            started_at=body.started_at or utc_now(),
            ended_at=body.ended_at or utc_now(),
        )
        db.add(session)
        db.flush()

        for item in body.items:
            db.add(
                PracticeSessionItem(
                    session_id=session.id,
                    question_id=item.question_id,
                    knowledge_point_id=item.knowledge_point_id or q_map[item.question_id].knowledge_point_id,
                    user_answer=item.user_answer,
                    is_correct=item.is_correct,
                    duration_seconds=item.duration_seconds,
                )
            )
        db.commit()
        db.refresh(session)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="保存练习记录失败，请稍后重试") from exc
    return _build_session_response(db, session, include_items=True)


@router.get("", response_model=PracticeSessionListResponse)
def list_practice_sessions(
    page: int = 1,
    page_size: int = 20,
    mode: str | None = None,
    db: Session = Depends(get_db),
):
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100

    query = db.query(PracticeSession)
    if mode:
        query = query.filter(PracticeSession.mode == mode)
    total = query.count()
    rows = query.order_by(PracticeSession.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    kb_ids = [row.knowledge_base_id for row in rows if row.knowledge_base_id]
    kb_map = {
        kb.id: kb.name
        for kb in db.query(KnowledgeBase).filter(KnowledgeBase.id.in_(kb_ids)).all()
    } if kb_ids else {}
    return PracticeSessionListResponse(
        items=[
            _build_session_response(
                db,
                row,
                include_items=False,
                knowledge_base_name=kb_map.get(row.knowledge_base_id),
            )
            for row in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{session_id}", response_model=PracticeSessionResponse)
def get_practice_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="练习会话不存在")
    return _build_session_response(db, session, include_items=True)
