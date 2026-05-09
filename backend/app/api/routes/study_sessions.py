from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.study_session import StudySession
from ...models.knowledge_base import KnowledgeBase
from ...models.knowledge_point import KnowledgePoint
from ...schemas.study_session import StudySessionCreate, StudySessionFinish, StudySessionResponse

router = APIRouter(prefix="/api/study-sessions", tags=["study-sessions"])


def _validate_targets(db: Session, knowledge_base_id: int | None, knowledge_point_id: int | None):
    if knowledge_base_id:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")

    if knowledge_point_id:
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
        if not kp:
            raise HTTPException(status_code=404, detail="知识点不存在")


@router.post("", response_model=StudySessionResponse)
def create_study_session(body: StudySessionCreate, db: Session = Depends(get_db)):
    _validate_targets(db, body.knowledge_base_id, body.knowledge_point_id)

    session = StudySession(
        knowledge_base_id=body.knowledge_base_id,
        knowledge_point_id=body.knowledge_point_id,
        total_count=body.total_count,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/finish", response_model=StudySessionResponse)
def finish_study_session(session_id: int, body: StudySessionFinish, db: Session = Depends(get_db)):
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="学习会话不存在")

    correct_count = min(body.correct_count, body.total_count)
    session.total_count = body.total_count
    session.correct_count = correct_count
    session.accuracy_rate = round(correct_count / body.total_count * 100, 1) if body.total_count else 0
    session.ended_at = datetime.utcnow()

    db.commit()
    db.refresh(session)
    return session
