from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, case, distinct
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.answer_record import AnswerRecord
from ...models.wrong_question import WrongQuestion
from ...models.audio_file import AudioFile
from ...models.knowledge_base import KnowledgeBase
from ...models.knowledge_point import KnowledgePoint
from ...models.question import Question
from ...models.review_task import ReviewTask
from ...utils.time import utc_today_start

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    today = utc_today_start()

    # 今日答题
    today_answers = db.query(AnswerRecord).filter(AnswerRecord.answered_at >= today).count()
    today_correct = db.query(AnswerRecord).filter(
        AnswerRecord.answered_at >= today, AnswerRecord.is_correct == True
    ).count()

    # 总答题
    total_answers = db.query(AnswerRecord).count()
    total_correct = db.query(AnswerRecord).filter(AnswerRecord.is_correct == True).count()
    accuracy = round(total_correct / total_answers * 100, 1) if total_answers > 0 else 0

    # 错题
    pending_review = db.query(WrongQuestion).filter(WrongQuestion.is_mastered == False).count()
    wrong_total = db.query(WrongQuestion).count()
    mastered_count = db.query(WrongQuestion).filter(WrongQuestion.is_mastered == True).count()

    # 复习任务
    review_pending = db.query(ReviewTask).filter(ReviewTask.status == "pending").count()
    review_completed = db.query(ReviewTask).filter(ReviewTask.status == "completed").count()
    review_total = db.query(ReviewTask).count()

    # 音频
    audio_success = db.query(AudioFile).filter(AudioFile.status == "success").count()
    audio_failed = db.query(AudioFile).filter(AudioFile.status == "failed").count()

    # 知识点：有题目覆盖的知识点 / 总知识点（粗略掌握度分母）
    total_kp = db.query(KnowledgePoint).count()
    kp_with_questions = db.query(distinct(Question.knowledge_point_id)).count()
    kp_coverage = round(kp_with_questions / total_kp * 100, 1) if total_kp > 0 else 0

    return {
        # 答题统计
        "today_answers": today_answers,
        "today_correct": today_correct,
        "total_answers": total_answers,
        "total_correct": total_correct,
        "accuracy": accuracy,
        # 错题统计
        "pending_review": pending_review,
        "wrong_total": wrong_total,
        "mastered_count": mastered_count,
        # 复习任务
        "review_pending": review_pending,
        "review_completed": review_completed,
        "review_total": review_total,
        # 知识点覆盖
        "total_knowledge_points": total_kp,
        "kp_with_questions": kp_with_questions,
        "kp_coverage": kp_coverage,
        # 音频
        "audio_success": audio_success,
        "audio_failed": audio_failed,
    }


@router.get("/knowledge-bases")
def get_knowledge_base_stats(db: Session = Depends(get_db)):
    kbs = db.query(KnowledgeBase).all()
    result = []
    for kb in kbs:
        kp_count = db.query(KnowledgePoint).filter(
            KnowledgePoint.knowledge_base_id == kb.id
        ).count()
        q_count = db.query(Question).filter(
            Question.knowledge_base_id == kb.id
        ).count()

        # 该知识库下的答题记录（通过 question 关联）
        kb_answer_count = db.query(AnswerRecord).join(
            Question, AnswerRecord.question_id == Question.id
        ).filter(Question.knowledge_base_id == kb.id).count()

        kb_correct_count = db.query(AnswerRecord).join(
            Question, AnswerRecord.question_id == Question.id
        ).filter(
            Question.knowledge_base_id == kb.id,
            AnswerRecord.is_correct == True
        ).count()

        kb_accuracy = round(kb_correct_count / kb_answer_count * 100, 1) if kb_answer_count > 0 else 0

        # 错题数
        kb_wrong_count = db.query(WrongQuestion).join(
            Question, WrongQuestion.question_id == Question.id
        ).filter(Question.knowledge_base_id == kb.id).count()

        # 未掌握错题
        kb_pending_wrong = db.query(WrongQuestion).join(
            Question, WrongQuestion.question_id == Question.id
        ).filter(
            Question.knowledge_base_id == kb.id,
            WrongQuestion.is_mastered == False
        ).count()

        # 复习任务
        kb_review_pending = db.query(ReviewTask).join(
            KnowledgePoint, ReviewTask.knowledge_point_id == KnowledgePoint.id
        ).filter(KnowledgePoint.knowledge_base_id == kb.id, ReviewTask.status == "pending").count()

        # 粗略掌握度 = 正确率 * 0.6 + 知识点覆盖率 * 0.4
        kp_with_q = db.query(distinct(Question.knowledge_point_id)).filter(
            Question.knowledge_base_id == kb.id
        ).count()
        coverage = round(kp_with_q / kp_count * 100, 1) if kp_count > 0 else 0
        mastery = round(kb_accuracy * 0.6 + coverage * 0.4, 1) if kb_answer_count > 0 else coverage

        result.append({
            "id": kb.id,
            "name": kb.name,
            "knowledge_point_count": kp_count,
            "question_count": q_count,
            "answer_count": kb_answer_count,
            "correct_count": kb_correct_count,
            "accuracy": kb_accuracy,
            "wrong_count": kb_wrong_count,
            "pending_wrong": kb_pending_wrong,
            "review_pending": kb_review_pending,
            "mastery": mastery,
        })
    return result


@router.get("/trends")
def get_trends(days: int = 7, db: Session = Depends(get_db)):
    today = utc_today_start()
    trends = []
    for i in range(days - 1, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        answers = db.query(AnswerRecord).filter(
            AnswerRecord.answered_at >= day_start,
            AnswerRecord.answered_at < day_end,
        ).count()

        correct = db.query(AnswerRecord).filter(
            AnswerRecord.answered_at >= day_start,
            AnswerRecord.answered_at < day_end,
            AnswerRecord.is_correct == True,
        ).count()

        accuracy = round(correct / answers * 100, 1) if answers > 0 else 0

        trends.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "answers": answers,
            "correct": correct,
            "accuracy": accuracy,
        })
    return trends
