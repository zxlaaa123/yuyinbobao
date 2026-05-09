import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
from ...core.database import get_db
from ...models.knowledge_point import KnowledgePoint
from ...models.question import Question
from ...models.wrong_question import WrongQuestion
from ...models.knowledge_base import KnowledgeBase

router = APIRouter(prefix="/api/export", tags=["export"])


def _csv_rows(headers: list[str], rows: list[list[str]]) -> str:
    """生成带 BOM 的 UTF-8 CSV 字符串，解决中文乱码"""
    buf = io.StringIO()
    buf.write("﻿")  # BOM
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def _get_kb_map(db: Session) -> dict[int, str]:
    return {kb.id: kb.name for kb in db.query(KnowledgeBase).all()}


@router.get("/knowledge-points.csv")
def export_knowledge_points_csv(
    knowledge_base_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgePoint)
    if knowledge_base_id:
        query = query.filter(KnowledgePoint.knowledge_base_id == knowledge_base_id)
    kps = query.order_by(KnowledgePoint.id.desc()).all()

    if not kps:
        raise HTTPException(status_code=400, detail="没有可导出的知识点")

    kb_map = _get_kb_map(db)

    def load_json(value: str | None) -> list:
        if not value:
            return []
        try:
            return json.loads(value)
        except Exception:
            return []

    headers = ["ID", "知识点标题", "摘要", "详细解释", "高频考点", "易混点", "记忆方法", "示例", "重要程度", "标签", "知识库", "题目数", "创建时间"]
    rows = []
    for kp in kps:
        rows.append([
            str(kp.id),
            kp.title or "",
            kp.summary or "",
            kp.detail or "",
            "; ".join(load_json(kp.exam_points)),
            "; ".join(load_json(kp.confusing_points)),
            "; ".join(load_json(kp.memory_tips)),
            "; ".join(load_json(kp.examples)),
            kp.importance or "medium",
            "; ".join(load_json(kp.tags)),
            kb_map.get(kp.knowledge_base_id, ""),
            str(db.query(Question).filter(Question.knowledge_point_id == kp.id).count()),
            str(kp.created_at) if kp.created_at else "",
        ])

    csv_content = _csv_rows(headers, rows)
    return StreamingResponse(
        iter([csv_content.encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=knowledge_points.csv"},
    )


@router.get("/questions.csv")
def export_questions_csv(
    knowledge_base_id: int | None = None,
    knowledge_point_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Question)
    if knowledge_base_id:
        query = query.filter(Question.knowledge_base_id == knowledge_base_id)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    questions = query.order_by(Question.id.desc()).all()

    if not questions:
        raise HTTPException(status_code=400, detail="没有可导出的题目")

    kb_map = _get_kb_map(db)
    kp_map = {kp.id: kp.title for kp in db.query(KnowledgePoint).all()}

    headers = ["ID", "题型", "题干", "选项", "答案", "解析", "难度", "知识点", "知识库", "创建时间"]
    rows = []
    for q in questions:
        opts = json.loads(q.options) if q.options else []
        opts_str = "; ".join(f"{o.get('key', '')}. {o.get('text', '')}" for o in opts)
        rows.append([
            str(q.id),
            q.question_type or "",
            q.stem or "",
            opts_str,
            q.answer or "",
            q.analysis or "",
            q.difficulty or "medium",
            kp_map.get(q.knowledge_point_id, ""),
            kb_map.get(q.knowledge_base_id, ""),
            str(q.created_at) if q.created_at else "",
        ])

    csv_content = _csv_rows(headers, rows)
    return StreamingResponse(
        iter([csv_content.encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=questions.csv"},
    )


@router.get("/wrong-questions.csv")
def export_wrong_questions_csv(
    knowledge_base_id: int | None = None,
    is_mastered: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(WrongQuestion)
    if is_mastered is not None:
        query = query.filter(WrongQuestion.is_mastered == is_mastered)
    wqs = query.order_by(WrongQuestion.last_wrong_at.desc()).all()

    if not wqs:
        raise HTTPException(status_code=400, detail="没有可导出的错题")

    kb_map = _get_kb_map(db)
    kp_map = {kp.id: kp.title for kp in db.query(KnowledgePoint).all()}

    headers = ["ID", "题干", "题型", "选项", "正确答案", "解析", "难度", "错误次数", "上次错误答案", "是否掌握", "知识点", "知识库", "上次错误时间"]
    rows = []
    for wq in wqs:
        q = db.query(Question).filter(Question.id == wq.question_id).first()
        if not q:
            continue
        if knowledge_base_id and q.knowledge_base_id != knowledge_base_id:
            continue
        opts = json.loads(q.options) if q.options else []
        opts_str = "; ".join(f"{o.get('key', '')}. {o.get('text', '')}" for o in opts)
        rows.append([
            str(wq.id),
            q.stem or "",
            q.question_type or "",
            opts_str,
            q.answer or "",
            q.analysis or "",
            q.difficulty or "medium",
            str(wq.wrong_count),
            wq.last_wrong_answer or "",
            "是" if wq.is_mastered else "否",
            kp_map.get(q.knowledge_point_id, ""),
            kb_map.get(q.knowledge_base_id, ""),
            str(wq.last_wrong_at) if wq.last_wrong_at else "",
        ])

    if not rows:
        raise HTTPException(status_code=400, detail="没有可导出的错题")

    csv_content = _csv_rows(headers, rows)
    return StreamingResponse(
        iter([csv_content.encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=wrong_questions.csv"},
    )
