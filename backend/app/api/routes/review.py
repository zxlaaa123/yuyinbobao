from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from ...core.database import get_db
from ...models.knowledge_point import KnowledgePoint
from ...services.review_service import (
    get_tasks,
    get_task_by_id,
    delete_task,
    complete_task,
    snooze_task,
    generate_tasks,
)

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/tasks")
def list_tasks(
    status: str | None = Query(None, description="筛选状态: pending / completed"),
    knowledge_base_id: int | None = Query(None, description="按知识库筛选"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return get_tasks(db, status=status, knowledge_base_id=knowledge_base_id, limit=limit, offset=offset)


@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/tasks/generate")
def generate(
    max_tasks: int = Query(30, ge=1, le=100, description="最多生成任务数"),
    db: Session = Depends(get_db),
):
    result = generate_tasks(db, max_tasks=max_tasks)
    return result


@router.post("/tasks/{task_id}/complete")
def complete(
    task_id: int,
    quality: str = Query("good", description="复习质量: again / hard / good / easy"),
    db: Session = Depends(get_db),
):
    if quality not in ("again", "hard", "good", "easy"):
        raise HTTPException(status_code=400, detail="quality 必须是 again / hard / good / easy 之一")
    try:
        task = complete_task(db, task_id, quality=quality)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == task.knowledge_point_id).first()
    return {
        "id": task.id,
        "knowledge_point_id": task.knowledge_point_id,
        "kp_title": kp.title if kp else "",
        "kp_summary": kp.summary or "" if kp else "",
        "source": task.source,
        "status": task.status,
        "difficulty": task.difficulty,
        "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "snooze_count": task.snooze_count,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


@router.post("/tasks/{task_id}/snooze")
def snooze(
    task_id: int,
    hours: int = Query(24, ge=1, le=720, description="推迟小时数"),
    db: Session = Depends(get_db),
):
    try:
        task = snooze_task(db, task_id, hours=hours)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == task.knowledge_point_id).first()
    return {
        "id": task.id,
        "knowledge_point_id": task.knowledge_point_id,
        "kp_title": kp.title if kp else "",
        "kp_summary": kp.summary or "" if kp else "",
        "source": task.source,
        "status": task.status,
        "difficulty": task.difficulty,
        "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "snooze_count": task.snooze_count,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


@router.delete("/tasks/{task_id}")
def delete(task_id: int, db: Session = Depends(get_db)):
    ok = delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"success": True, "message": "任务已删除"}
