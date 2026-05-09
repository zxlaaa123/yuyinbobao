from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select
from ..models.review_task import ReviewTask
from ..models.knowledge_point import KnowledgePoint
from ..models.wrong_question import WrongQuestion
from ..models.question import Question


REVIEW_BUCKETS = {"today", "overdue", "later", "completed"}


def get_today_review_overview(db: Session, knowledge_base_id: int | None = None, limit: int = 100) -> dict:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    base_query = db.query(KnowledgePoint)
    if knowledge_base_id:
        base_query = base_query.filter(KnowledgePoint.knowledge_base_id == knowledge_base_id)

    due_query = base_query.filter(
        KnowledgePoint.next_review_at.isnot(None),
        KnowledgePoint.next_review_at < tomorrow_start,
        KnowledgePoint.review_status.in_(["new", "learning", "review"]),
    )
    overdue_query = due_query.filter(KnowledgePoint.next_review_at < today_start)
    weak_query = base_query.filter(
        KnowledgePoint.review_status != "mastered",
        or_(
            KnowledgePoint.review_status == "learning",
            KnowledgePoint.wrong_streak > 0,
        ),
    )

    due_count = due_query.count()
    overdue_count = overdue_query.count()
    weak_count = weak_query.count()

    items = (
        due_query.order_by(
            KnowledgePoint.next_review_at.asc().nullslast(),
            KnowledgePoint.id.desc(),
        )
        .limit(limit)
        .all()
    )

    return {
        "due_count": due_count,
        "overdue_count": overdue_count,
        "weak_count": weak_count,
        "items": [
            {
                "knowledge_point_id": kp.id,
                "knowledge_base_id": kp.knowledge_base_id,
                "title": kp.title,
                "summary": kp.summary or "",
                "review_status": kp.review_status,
                "mastery_level": kp.mastery_level,
                "review_count": kp.review_count,
                "correct_streak": kp.correct_streak,
                "wrong_streak": kp.wrong_streak,
                "last_reviewed_at": kp.last_reviewed_at.isoformat() if kp.last_reviewed_at else None,
                "next_review_at": kp.next_review_at.isoformat() if kp.next_review_at else None,
                "is_overdue": bool(kp.next_review_at and kp.next_review_at < today_start),
            }
            for kp in items
        ],
    }


def _review_bucket(task: ReviewTask, now: datetime | None = None) -> str:
    if task.status == "completed":
        return "completed"

    now = now or datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    scheduled_at = task.scheduled_at or now

    if scheduled_at < today:
        return "overdue"
    if scheduled_at < tomorrow:
        return "today"
    return "later"


def _next_interval_days(quality: str, review_count: int) -> int:
    base = {"again": 1, "hard": 2, "good": 4, "easy": 7}.get(quality, 4)
    if quality == "again":
        return base
    return base * max(review_count, 1)


def _task_to_response(task: ReviewTask, kp: KnowledgePoint, now: datetime | None = None) -> dict:
    return {
        "id": task.id,
        "knowledge_point_id": task.knowledge_point_id,
        "kp_title": kp.title,
        "kp_summary": kp.summary or "",
        "source": task.source,
        "status": task.status,
        "review_bucket": _review_bucket(task, now),
        "difficulty": task.difficulty,
        "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "last_reviewed_at": task.last_reviewed_at.isoformat() if task.last_reviewed_at else None,
        "last_quality": task.last_quality,
        "review_count": task.review_count,
        "next_interval_days": task.next_interval_days,
        "snooze_count": task.snooze_count,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


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
    if status and status not in REVIEW_BUCKETS:
        query = query.filter(ReviewTask.status == status)
    elif status == "completed":
        query = query.filter(ReviewTask.status == "completed")
    elif status in {"today", "overdue", "later"}:
        query = query.filter(ReviewTask.status == "pending")
    if knowledge_base_id:
        query = query.filter(KnowledgePoint.knowledge_base_id == knowledge_base_id)
    rows = query.order_by(ReviewTask.scheduled_at.asc().nullslast(), ReviewTask.created_at.asc()).all()

    now = datetime.utcnow()
    result = [_task_to_response(task, kp, now) for task, kp in rows]
    if status in REVIEW_BUCKETS:
        result = [item for item in result if item["review_bucket"] == status]
    return result[offset: offset + limit]


def get_task_by_id(db: Session, task_id: int) -> dict | None:
    row = db.query(ReviewTask, KnowledgePoint).join(
        KnowledgePoint, ReviewTask.knowledge_point_id == KnowledgePoint.id
    ).filter(ReviewTask.id == task_id).first()
    if not row:
        return None
    task, kp = row
    return _task_to_response(task, kp)


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
    next_review_count = task.review_count + 1
    interval_days = _next_interval_days(quality, next_review_count)
    task.status = "pending" if quality == "again" else "completed"
    task.completed_at = now
    task.last_reviewed_at = now
    task.last_quality = quality
    task.review_count = next_review_count
    task.next_interval_days = interval_days
    task.scheduled_at = now + timedelta(days=interval_days)

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
    wrong_question_ids = (
        select(WrongQuestion.question_id)
        .filter(WrongQuestion.is_mastered == False)
    )
    wrong_kp_ids = (
        select(Question.knowledge_point_id)
        .filter(Question.id.in_(wrong_question_ids))
        .distinct()
    )

    # 排除已有 pending 任务的知识点
    pending_kp_ids = (
        select(ReviewTask.knowledge_point_id)
        .filter(ReviewTask.status == "pending")
        .distinct()
    )

    wrong_kps = (
        db.query(KnowledgePoint)
        .filter(
            KnowledgePoint.id.in_(wrong_kp_ids),
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
