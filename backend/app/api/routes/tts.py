import sys
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.config import (
    TTS_PROVIDER,
    XIAOMI_TTS_API_KEY, XIAOMI_TTS_BASE_URL, XIAOMI_TTS_VOICE, XIAOMI_TTS_FORMAT,
)
from ...services.setting_service import get_all_settings
from ...models.knowledge_point import KnowledgePoint
from ...models.audio_file import AudioFile
from ...models.review_task import ReviewTask
from ...models.wrong_question import WrongQuestion
from ...models.question import Question
from ...services.tts_service import build_text_from_knowledge_point, build_text_from_knowledge_points, synthesize_audio, normalize_audio_format
from ...services.audio_service import generate_audio_filename, generate_collection_filename, save_audio_file, build_file_url

router = APIRouter(prefix="/api/tts", tags=["tts"])


@router.post("/generate")
async def generate_audio(body: dict, db: Session = Depends(get_db)):
    print("=" * 50, flush=True)
    print("TTS generate called", flush=True)

    kp_id = body.get("knowledge_point_id")
    if not kp_id:
        raise HTTPException(status_code=400, detail="缺少 knowledge_point_id")

    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    print(f"找到知识点: {kp.title}", flush=True)

    # 构建播报文本
    text_content = build_text_from_knowledge_point(kp)
    print(f"播报文本长度: {len(text_content)}", flush=True)

    settings = get_all_settings(db)
    audio_ext = normalize_audio_format(settings.get("XIAOMI_TTS_FORMAT", XIAOMI_TTS_FORMAT))
    filename = generate_audio_filename(kp.id, ext=audio_ext)
    print(f"文件名: {filename}", flush=True)

    audio_record = AudioFile(
        knowledge_point_id=kp.id,
        title=kp.title,
        text_content=text_content,
        file_path=str(filename),
        file_url=build_file_url(filename),
        status="pending",
    )
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)
    print(f"audio_record 创建成功, id={audio_record.id}", flush=True)

    # 获取 TTS 配置（优先数据库，回退 .env）
    provider = settings.get("TTS_PROVIDER", TTS_PROVIDER)
    xiaomi_key = settings.get("XIAOMI_TTS_API_KEY", XIAOMI_TTS_API_KEY)
    xiaomi_base = settings.get("XIAOMI_TTS_BASE_URL", XIAOMI_TTS_BASE_URL)
    xiaomi_voice = settings.get("XIAOMI_TTS_VOICE", XIAOMI_TTS_VOICE)
    print(f"配置: provider={provider}, format={audio_ext}, base_configured={bool(xiaomi_base)}", flush=True)

    try:
        print("开始调用 synthesize_audio...", flush=True)
        audio_bytes = await synthesize_audio(
            text_content,
            provider=provider,
            api_key=xiaomi_key,
            base_url=xiaomi_base,
            voice=xiaomi_voice,
            audio_format=audio_ext,
        )
        print(f"synthesize_audio 成功, 音频大小: {len(audio_bytes)} bytes", flush=True)

        file_path = save_audio_file(filename, audio_bytes)
        print(f"音频文件保存成功: {file_path}", flush=True)

        audio_record.status = "success"
        audio_record.file_path = file_path
        db.commit()
        db.refresh(audio_record)
        print("audio_record 更新成功", flush=True)

        return {
            "audio_id": audio_record.id,
            "knowledge_point_id": kp.id,
            "title": kp.title,
            "status": "success",
            "file_url": audio_record.file_url,
        }
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"TTS ERROR: {error_detail}", flush=True)
        print(traceback.format_exc(), flush=True)
        audio_record.status = "failed"
        audio_record.error_message = error_detail
        db.commit()
        raise HTTPException(status_code=500, detail=f"TTS 生成失败：{error_detail}")


TTS_BATCH_MAX_POINTS = 20
TTS_BATCH_MAX_CHARS = 5000


@router.post("/generate-batch")
async def generate_batch(body: dict, db: Session = Depends(get_db)):
    kp_ids = body.get("knowledge_point_ids", [])
    if not kp_ids or not isinstance(kp_ids, list):
        raise HTTPException(status_code=400, detail="缺少 knowledge_point_ids（数组）")

    if len(kp_ids) > TTS_BATCH_MAX_POINTS:
        raise HTTPException(status_code=400, detail=f"一次最多生成 {TTS_BATCH_MAX_POINTS} 个知识点的合集音频")

    # 查询所有知识点
    kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()
    if len(kps) != len(kp_ids):
        found_ids = {kp.id for kp in kps}
        missing = [i for i in kp_ids if i not in found_ids]
        raise HTTPException(status_code=404, detail=f"知识点不存在: {missing}")

    # 构建合集播报文本
    text_content = build_text_from_knowledge_points(kps)

    if len(text_content) > TTS_BATCH_MAX_CHARS:
        raise HTTPException(status_code=400, detail=f"合集文本过长（{len(text_content)} 字符），超过上限 {TTS_BATCH_MAX_CHARS}，请减少知识点数量")

    settings = get_all_settings(db)
    audio_ext = normalize_audio_format(settings.get("XIAOMI_TTS_FORMAT", XIAOMI_TTS_FORMAT))
    filename = generate_collection_filename(kp_ids, ext=audio_ext)

    titles = "、".join(kp.title for kp in kps)
    if len(titles) > 100:
        titles = titles[:100] + "..."

    audio_record = AudioFile(
        knowledge_point_id=kps[0].id,
        title=f"合集音频（{len(kps)} 个知识点）",
        text_content=text_content,
        file_path=str(filename),
        file_url=build_file_url(filename),
        status="pending",
    )
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)

    # 获取 TTS 配置（优先数据库，回退 .env）
    provider = settings.get("TTS_PROVIDER", TTS_PROVIDER)
    xiaomi_key = settings.get("XIAOMI_TTS_API_KEY", XIAOMI_TTS_API_KEY)
    xiaomi_base = settings.get("XIAOMI_TTS_BASE_URL", XIAOMI_TTS_BASE_URL)
    xiaomi_voice = settings.get("XIAOMI_TTS_VOICE", XIAOMI_TTS_VOICE)

    try:
        audio_bytes = await synthesize_audio(
            text_content,
            provider=provider,
            api_key=xiaomi_key,
            base_url=xiaomi_base,
            voice=xiaomi_voice,
            audio_format=audio_ext,
        )
        file_path = save_audio_file(filename, audio_bytes)
        audio_record.status = "success"
        audio_record.file_path = file_path
        db.commit()
        db.refresh(audio_record)
        return {
            "audio_id": audio_record.id,
            "title": audio_record.title,
            "knowledge_point_count": len(kps),
            "status": "success",
            "file_url": audio_record.file_url,
        }
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"TTS BATCH ERROR: {error_detail}", flush=True)
        print(traceback.format_exc(), flush=True)
        audio_record.status = "failed"
        audio_record.error_message = error_detail
        db.commit()
        raise HTTPException(status_code=500, detail=f"合集音频生成失败：{error_detail}")


async def _generate_collection_audio(db: Session, kps: list[KnowledgePoint], title_prefix: str) -> dict:
    """通用合集音频生成逻辑"""
    kp_ids = [kp.id for kp in kps]
    text_content = build_text_from_knowledge_points(kps)

    if len(text_content) > TTS_BATCH_MAX_CHARS:
        raise HTTPException(status_code=400, detail=f"合集文本过长（{len(text_content)} 字符），超过上限 {TTS_BATCH_MAX_CHARS}")

    settings = get_all_settings(db)
    audio_ext = normalize_audio_format(settings.get("XIAOMI_TTS_FORMAT", XIAOMI_TTS_FORMAT))
    filename = generate_collection_filename(kp_ids, ext=audio_ext)

    audio_record = AudioFile(
        knowledge_point_id=kps[0].id,
        title=f"{title_prefix}（{len(kps)} 个知识点）",
        text_content=text_content,
        file_path=str(filename),
        file_url=build_file_url(filename),
        status="pending",
    )
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)

    provider = settings.get("TTS_PROVIDER", TTS_PROVIDER)
    xiaomi_key = settings.get("XIAOMI_TTS_API_KEY", XIAOMI_TTS_API_KEY)
    xiaomi_base = settings.get("XIAOMI_TTS_BASE_URL", XIAOMI_TTS_BASE_URL)
    xiaomi_voice = settings.get("XIAOMI_TTS_VOICE", XIAOMI_TTS_VOICE)

    try:
        audio_bytes = await synthesize_audio(
            text_content,
            provider=provider,
            api_key=xiaomi_key,
            base_url=xiaomi_base,
            voice=xiaomi_voice,
            audio_format=audio_ext,
        )
        file_path = save_audio_file(filename, audio_bytes)
        audio_record.status = "success"
        audio_record.file_path = file_path
        db.commit()
        db.refresh(audio_record)
        return {
            "audio_id": audio_record.id,
            "title": audio_record.title,
            "knowledge_point_count": len(kps),
            "status": "success",
            "file_url": audio_record.file_url,
        }
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        audio_record.status = "failed"
        audio_record.error_message = error_detail
        db.commit()
        raise HTTPException(status_code=500, detail=f"音频生成失败：{error_detail}")


@router.post("/generate-daily-review")
async def generate_daily_review(body: dict, db: Session = Depends(get_db)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 查找今日 pending 复习任务
    pending_tasks = (
        db.query(ReviewTask)
        .filter(ReviewTask.status == "pending", ReviewTask.created_at >= today)
        .all()
    )

    if not pending_tasks:
        raise HTTPException(status_code=400, detail="今日暂无待复习任务，请先生成复习任务")

    kp_ids = [t.knowledge_point_id for t in pending_tasks]
    kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()

    if not kps:
        raise HTTPException(status_code=404, detail="复习任务关联的知识点不存在")

    return await _generate_collection_audio(db, kps, "每日复习音频")


@router.post("/generate-wrong-questions")
async def generate_wrong_questions(body: dict, db: Session = Depends(get_db)):
    wq_ids = body.get("wrong_question_ids", [])

    if not wq_ids or not isinstance(wq_ids, list):
        raise HTTPException(status_code=400, detail="缺少 wrong_question_ids（数组）")

    if len(wq_ids) > TTS_BATCH_MAX_POINTS:
        raise HTTPException(status_code=400, detail=f"一次最多生成 {TTS_BATCH_MAX_POINTS} 个错题的音频")

    # 通过错题记录找到关联的知识点
    wqs = db.query(WrongQuestion).filter(WrongQuestion.id.in_(wq_ids)).all()
    if len(wqs) != len(wq_ids):
        found_ids = {wq.id for wq in wqs}
        missing = [i for i in wq_ids if i not in found_ids]
        raise HTTPException(status_code=404, detail=f"错题记录不存在: {missing}")

    # 通过题目找到知识点
    question_ids = [wq.question_id for wq in wqs]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    kp_ids = list({q.knowledge_point_id for q in questions})
    kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()

    if not kps:
        raise HTTPException(status_code=404, detail="错题关联的知识点不存在")

    return await _generate_collection_audio(db, kps, "错题复习音频")
