from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.knowledge_point import KnowledgePoint
from ...models.knowledge_base import KnowledgeBase
from ...models.material import Material
from ...models.question import Question
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion
from ...models.audio_file import AudioFile
from ...models.review_task import ReviewTask
from ...schemas.knowledge_point import KnowledgePointUpdate
from ...services.audio_service import delete_audio_file
from ...utils.json_helpers import dump_json as _dump_json
from ...utils.json_helpers import load_json as _load_json

router = APIRouter(prefix="/api/knowledge-points", tags=["knowledge-points"])


def _to_list_response(kp: KnowledgePoint, kb_name: str = "", mat_title: str = "") -> dict:
    return {
        "id": kp.id,
        "knowledge_base_id": kp.knowledge_base_id,
        "knowledge_base_name": kb_name,
        "material_id": kp.material_id,
        "title": kp.title,
        "summary": kp.summary,
        "importance": kp.importance,
        "tags": _load_json(kp.tags),
        "mastery_level": kp.mastery_level,
        "review_count": kp.review_count,
        "correct_streak": kp.correct_streak,
        "wrong_streak": kp.wrong_streak,
        "last_reviewed_at": kp.last_reviewed_at,
        "next_review_at": kp.next_review_at,
        "review_status": kp.review_status,
        "question_count": 0,
        "audio_count": 0,
        "created_at": kp.created_at,
        "updated_at": kp.updated_at,
    }


def _to_detail_response(kp: KnowledgePoint, kb_name: str = "", mat_title: str = "") -> dict:
    return {
        "id": kp.id,
        "knowledge_base_id": kp.knowledge_base_id,
        "knowledge_base_name": kb_name,
        "material_id": kp.material_id,
        "material_title": mat_title,
        "title": kp.title,
        "summary": kp.summary,
        "detail": kp.detail,
        "exam_points": _load_json(kp.exam_points),
        "confusing_points": _load_json(kp.confusing_points),
        "memory_tips": _load_json(kp.memory_tips),
        "examples": _load_json(kp.examples),
        "importance": kp.importance,
        "tags": _load_json(kp.tags),
        "mastery_level": kp.mastery_level,
        "review_count": kp.review_count,
        "correct_streak": kp.correct_streak,
        "wrong_streak": kp.wrong_streak,
        "last_reviewed_at": kp.last_reviewed_at,
        "next_review_at": kp.next_review_at,
        "review_status": kp.review_status,
        "question_count": 0,
        "audio_files": [],
        "created_at": kp.created_at,
        "updated_at": kp.updated_at,
    }


@router.get("")
def list_knowledge_points(
    knowledge_base_id: int | None = None,
    material_id: int | None = None,
    keyword: str | None = None,
    importance: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgePoint)
    if knowledge_base_id:
        query = query.filter(KnowledgePoint.knowledge_base_id == knowledge_base_id)
    if material_id:
        query = query.filter(KnowledgePoint.material_id == material_id)
    if importance:
        query = query.filter(KnowledgePoint.importance == importance)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(KnowledgePoint.title.ilike(kw) | KnowledgePoint.summary.ilike(kw))

    kps = query.order_by(KnowledgePoint.id.desc()).all()

    if tag:
        # 在 Python 层面过滤，避免 JSON 字段 ilike 误匹配
        tag_lower = tag.lower()
        kps = [kp for kp in kps if kp.tags and tag_lower in kp.tags.lower()]

    kp_ids = [kp.id for kp in kps]
    kb_ids = [kp.knowledge_base_id for kp in kps]
    mat_ids = [kp.material_id for kp in kps if kp.material_id]
    kb_map = {
        kb.id: kb.name
        for kb in db.query(KnowledgeBase).filter(KnowledgeBase.id.in_(kb_ids)).all()
    } if kb_ids else {}
    mat_map = {
        mat.id: mat.title
        for mat in db.query(Material).filter(Material.id.in_(mat_ids)).all()
    } if mat_ids else {}
    question_count_map = dict(
        db.query(Question.knowledge_point_id, func.count(Question.id))
        .filter(Question.knowledge_point_id.in_(kp_ids))
        .group_by(Question.knowledge_point_id)
        .all()
    ) if kp_ids else {}
    audio_count_map = dict(
        db.query(AudioFile.knowledge_point_id, func.count(AudioFile.id))
        .filter(AudioFile.knowledge_point_id.in_(kp_ids))
        .group_by(AudioFile.knowledge_point_id)
        .all()
    ) if kp_ids else {}

    result = []
    for kp in kps:
        item = _to_list_response(kp, kb_map.get(kp.knowledge_base_id, ""), mat_map.get(kp.material_id, ""))
        item["question_count"] = question_count_map.get(kp.id, 0)
        item["audio_count"] = audio_count_map.get(kp.id, 0)
        result.append(item)
    return result


@router.get("/{kp_id}")
def get_knowledge_point(kp_id: int, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kp.knowledge_base_id).first()
    mat = db.query(Material).filter(Material.id == kp.material_id).first() if kp.material_id else None
    audio_files = db.query(AudioFile).filter(AudioFile.knowledge_point_id == kp.id).all()
    result = _to_detail_response(kp, kb.name if kb else "", mat.title if mat else "")
    result["audio_files"] = [
        {"id": a.id, "title": a.title, "file_url": a.file_url, "status": a.status}
        for a in audio_files
    ]
    return result


@router.put("/{kp_id}")
def update_knowledge_point(kp_id: int, body: KnowledgePointUpdate, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    if body.title is not None:
        if not body.title.strip():
            raise HTTPException(status_code=400, detail="知识点标题不能为空")
        kp.title = body.title.strip()
    if body.summary is not None:
        kp.summary = body.summary
    if body.detail is not None:
        kp.detail = body.detail
    if body.exam_points is not None:
        kp.exam_points = _dump_json(body.exam_points)
    if body.confusing_points is not None:
        kp.confusing_points = _dump_json(body.confusing_points)
    if body.memory_tips is not None:
        kp.memory_tips = _dump_json(body.memory_tips)
    if body.examples is not None:
        kp.examples = _dump_json(body.examples)
    if body.importance is not None:
        if body.importance not in ("low", "medium", "high"):
            raise HTTPException(status_code=400, detail="importance 只能是 low、medium、high")
        kp.importance = body.importance
    if body.tags is not None:
        kp.tags = _dump_json(body.tags)
    db.commit()
    db.refresh(kp)
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kp.knowledge_base_id).first()
    mat = db.query(Material).filter(Material.id == kp.material_id).first() if kp.material_id else None
    return _to_detail_response(kp, kb.name if kb else "", mat.title if mat else "")


@router.delete("/{kp_id}")
def delete_knowledge_point(kp_id: int, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    # 删除关联题目
    questions = db.query(Question).filter(Question.knowledge_point_id == kp.id).all()
    for q in questions:
        db.query(AnswerRecord).filter(AnswerRecord.question_id == q.id).delete()
        db.query(WrongQuestion).filter(WrongQuestion.question_id == q.id).delete()
        db.delete(q)
    # 删除关联复习任务
    db.query(ReviewTask).filter(ReviewTask.knowledge_point_id == kp.id).delete()
    # 删除关联音频
    audio_files = db.query(AudioFile).filter(AudioFile.knowledge_point_id == kp.id).all()
    for audio in audio_files:
        if audio.file_path:
            delete_audio_file(audio.file_path)
        db.delete(audio)
    db.delete(kp)
    db.commit()
    return {"success": True, "message": "知识点已删除"}
