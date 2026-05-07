from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.review_task import ReviewTask
from ..models.knowledge_point import KnowledgePoint
from ..models.wrong_question import WrongQuestion
from ..models.question import Question


def get_tasks(
    db: Session,
    status: str | None = None,
    knowledge_base_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    query = db.query(ReviewTask, KnowledgePoint).join(
        KnowledgePoint, ReviewTask.knowledge_point_id == KnowledgePoint.id
    )
    if status:
        query = query.filter(ReviewTask.status == status)
    if knowledge_base_id:
        query = query.filter(KnowledgePoint.knowledge_base_id == knowledge_base_id)
    rows = query.order_by(
        ReviewTask.scheduled_at.asc().nullslast(), ReviewTask.created_at.asc()
    ).offset(offset).limit(limit).all()

    return [
        {
            "id": task.id,
            "knowledge_point_id": task.knowledge_point_id,
            "kp_title": kp.title,
            "kp_summary": kp.summary or "",
            "source": task.source,
            "status": task.status,
            "difficulty": task.difficulty,
            "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "snooze_count": task.snooze_count,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }
        for task, kp in rows
    ]


def get_task_by_id(db: Session, task_id: int) -> dict | None:
    row = db.query(ReviewTask, KnowledgePoint).join(
        KnowledgePoint, ReviewTask.knowledge_point_id == KnowledgePoint.id
    ).filter(ReviewTask.id == task_id).first()
    if not row:
        return None
    task, kp = row
    return {
        "id": task.id,
        "knowledge_point_id": task.knowledge_point_id,
        "kp_title": kp.title,
        "kp_summary": kp.summary or "",
        "source": task.source,
        "status": task.status,
        "difficulty": task.difficulty,
        "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "snooze_count": task.snooze_count,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(ReviewTask).filter(ReviewTask.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def complete_task(db: Session, task_id: int, quality: str = "good") -> ReviewTask:
    task = db.query(ReviewTask).filter(ReviewTask.id == task_id).first()
    if not task:
        raise ValueError("任务不存在")

    now = datetime.utcnow()
    task.status = "completed"
    task.completed_at = now

    # 简单间隔：again=1天, hard=2天, good=3天, easy=5天
    interval_map = {"again": 1, "hard": 2, "good": 3, "easy": 5}
    days = interval_map.get(quality, 3)
    task.scheduled_at = now + timedelta(days=days)

    # 如果是 again，重置为 pending
    if quality == "again":
        task.status = "pending"

    db.commit()
    db.refresh(task)
    return task


def snooze_task(db: Session, task_id: int, hours: int = 24) -> ReviewTask:
    task = db.query(ReviewTask).filter(ReviewTask.id == task_id).first()
    if not task:
        raise ValueError("任务不存在")

    task.snooze_count += 1
    task.scheduled_at = datetime.utcnow() + timedelta(hours=hours)
    db.commit()
    db.refresh(task)
    return task


def generate_tasks(db: Session, max_tasks: int = 30) -> dict:
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 检查今天是否已生成过 pending 任务
    existing = (
        db.query(ReviewTask)
        .filter(ReviewTask.status == "pending", ReviewTask.created_at >= today)
        .count()
    )
    if existing > 0:
        return {"created": 0, "message": f"今天已生成 {existing} 个待复习任务，不重复生成", "total_pending": existing}

    created = 0

    # 1. 错题优先：有错题记录且未掌握的知识点
    wrong_kp_ids = (
        db.query(WrongQuestion.question_id)
        .filter(WrongQuestion.is_mastered == False)
        .subquery()
    )
    wrong_kp_from_questions = (
        db.query(Question.knowledge_point_id)
        .filter(Question.id.in_(wrong_kp_ids))
        .distinct()
        .subquery()
    )

    # 排除已有 pending 任务的知识点
    pending_kp_ids = (
        db.query(ReviewTask.knowledge_point_id)
        .filter(ReviewTask.status == "pending")
        .distinct()
        .subquery()
    )

    wrong_kps = (
        db.query(KnowledgePoint)
        .filter(
            KnowledgePoint.id.in_(wrong_kp_from_questions),
            ~KnowledgePoint.id.in_(pending_kp_ids),
        )
        .limit(max_tasks)
        .all()
    )

    for kp in wrong_kps:
        task = ReviewTask(
            knowledge_point_id=kp.id,
            source="wrong_question",
            status="pending",
            difficulty="medium",
        )
        db.add(task)
        created += 1

    if created >= max_tasks:
        db.commit()
        return {"created": created, "total_pending": existing + created}

    # 2. high 重要知识点
    remaining = max_tasks - created
    high_kps = (
        db.query(KnowledgePoint)
        .filter(
            KnowledgePoint.importance == "high",
            ~KnowledgePoint.id.in_(pending_kp_ids),
        )
        .order_by(KnowledgePoint.created_at.asc())
        .limit(remaining)
        .all()
    )

    for kp in high_kps:
        task = ReviewTask(
            knowledge_point_id=kp.id,
            source="importance_high",
            status="pending",
            difficulty="hard",
        )
        db.add(task)
        created += 1

    if created >= max_tasks:
        db.commit()
        return {"created": created, "total_pending": existing + created}

    # 3. 新知识点（最近创建的）
    remaining = max_tasks - created
    new_kps = (
        db.query(KnowledgePoint)
        .filter(~KnowledgePoint.id.in_(pending_kp_ids))
        .order_by(KnowledgePoint.created_at.desc())
        .limit(remaining)
        .all()
    )

    for kp in new_kps:
        task = ReviewTask(
            knowledge_point_id=kp.id,
            source="new_knowledge",
            status="pending",
            difficulty="easy",
        )
        db.add(task)
        created += 1

    db.commit()
    return {"created": created, "total_pending": existing + created}
