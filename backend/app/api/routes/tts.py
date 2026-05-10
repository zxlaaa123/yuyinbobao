from pathlib import Path
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.config import (
    TTS_PROVIDER,
    XIAOMI_TTS_API_KEY, XIAOMI_TTS_BASE_URL, XIAOMI_TTS_VOICE, XIAOMI_TTS_FORMAT,
    XIAOMI_TTS_MODEL, XIAOMI_TTS_STYLE_PROMPT,
)
from ...services.setting_service import get_all_settings
from ...models.knowledge_point import KnowledgePoint
from ...models.audio_file import AudioFile
from ...models.review_task import ReviewTask
from ...models.wrong_question import WrongQuestion
from ...models.question import Question
from ...services.tts_service import build_text_from_knowledge_point, build_text_from_knowledge_points, synthesize_audio, normalize_audio_format
from ...services.audio_service import delete_audio_file, generate_audio_filename, generate_collection_filename, save_audio_file, build_file_url
from ...utils.time import utc_today_start

router = APIRouter(prefix="/api/tts", tags=["tts"])


def _get_tts_config(db: Session) -> dict:
    settings = get_all_settings(db)
    audio_format = normalize_audio_format(settings.get("XIAOMI_TTS_FORMAT", XIAOMI_TTS_FORMAT))
    return {
        "provider": settings.get("TTS_PROVIDER", TTS_PROVIDER),
        "api_key": settings.get("XIAOMI_TTS_API_KEY", XIAOMI_TTS_API_KEY),
        "base_url": settings.get("XIAOMI_TTS_BASE_URL", XIAOMI_TTS_BASE_URL),
        "model": settings.get("XIAOMI_TTS_MODEL", XIAOMI_TTS_MODEL),
        "voice": settings.get("XIAOMI_TTS_VOICE", XIAOMI_TTS_VOICE),
        "audio_format": audio_format,
        "style_prompt": settings.get("XIAOMI_TTS_STYLE_PROMPT", XIAOMI_TTS_STYLE_PROMPT),
    }


async def _render_audio_record(db: Session, audio_record: AudioFile, filename: str, config: dict) -> AudioFile:
    try:
        audio_bytes = await synthesize_audio(
            audio_record.text_content,
            provider=config["provider"],
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            voice=config["voice"],
            audio_format=config["audio_format"],
            style_prompt=config["style_prompt"],
        )
        file_path = save_audio_file(filename, audio_bytes)
        audio_record.status = "success"
        audio_record.file_path = file_path
        audio_record.file_url = build_file_url(Path(filename).name)
        audio_record.file_size = len(audio_bytes)
        audio_record.error_message = None
        db.commit()
        db.refresh(audio_record)
        return audio_record
    except Exception:
        error_detail = "TTS 生成失败，请检查 TTS 配置或稍后重试"
        audio_record.status = "failed"
        audio_record.error_message = error_detail
        db.commit()
        raise HTTPException(status_code=500, detail=error_detail)


def _audio_response(audio_record: AudioFile, **extra) -> dict:
    data = {
        "audio_id": audio_record.id,
        "knowledge_point_id": audio_record.knowledge_point_id,
        "title": audio_record.title,
        "status": audio_record.status,
        "file_url": audio_record.file_url,
        "audio_type": audio_record.audio_type,
        "provider": audio_record.provider,
        "voice": audio_record.voice,
        "audio_format": audio_record.audio_format,
        "file_size": audio_record.file_size,
    }
    data.update(extra)
    return data


@router.post("/generate")
async def generate_audio(body: dict, db: Session = Depends(get_db)):
    kp_id = body.get("knowledge_point_id")
    if not kp_id:
        raise HTTPException(status_code=400, detail="缺少 knowledge_point_id")

    kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    # 构建播报文本
    text_content = build_text_from_knowledge_point(kp)

    config = _get_tts_config(db)
    audio_ext = config["audio_format"]
    filename = generate_audio_filename(kp.id, ext=audio_ext)

    audio_record = AudioFile(
        knowledge_point_id=kp.id,
        title=kp.title,
        text_content=text_content,
        file_path=str(filename),
        file_url=build_file_url(filename),
        audio_type="single",
        provider=config["provider"],
        voice=config["voice"],
        audio_format=audio_ext,
        status="pending",
    )
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)
    audio_record = await _render_audio_record(db, audio_record, filename, config)
    return _audio_response(audio_record)


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

    config = _get_tts_config(db)
    audio_ext = config["audio_format"]
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
        audio_type="collection",
        provider=config["provider"],
        voice=config["voice"],
        audio_format=audio_ext,
        status="pending",
    )
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)

    audio_record = await _render_audio_record(db, audio_record, filename, config)
    return _audio_response(audio_record, knowledge_point_count=len(kps))


async def _generate_collection_audio(db: Session, kps: list[KnowledgePoint], title_prefix: str, audio_type: str) -> dict:
    """通用合集音频生成逻辑"""
    kp_ids = [kp.id for kp in kps]
    text_content = build_text_from_knowledge_points(kps)

    if len(text_content) > TTS_BATCH_MAX_CHARS:
        raise HTTPException(status_code=400, detail=f"合集文本过长（{len(text_content)} 字符），超过上限 {TTS_BATCH_MAX_CHARS}")

    config = _get_tts_config(db)
    audio_ext = config["audio_format"]
    filename = generate_collection_filename(kp_ids, ext=audio_ext)

    audio_record = AudioFile(
        knowledge_point_id=kps[0].id,
        title=f"{title_prefix}（{len(kps)} 个知识点）",
        text_content=text_content,
        file_path=str(filename),
        file_url=build_file_url(filename),
        audio_type=audio_type,
        provider=config["provider"],
        voice=config["voice"],
        audio_format=audio_ext,
        status="pending",
    )
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)

    audio_record = await _render_audio_record(db, audio_record, filename, config)
    return _audio_response(audio_record, knowledge_point_count=len(kps))


@router.post("/generate-daily-review")
async def generate_daily_review(body: dict, db: Session = Depends(get_db)):
    today = utc_today_start()

    # 查找今日或逾期 pending 复习任务
    pending_tasks = (
        db.query(ReviewTask)
        .filter(
            ReviewTask.status == "pending",
            (ReviewTask.scheduled_at == None) | (ReviewTask.scheduled_at < today + timedelta(days=1)),
        )
        .all()
    )

    if not pending_tasks:
        raise HTTPException(status_code=400, detail="今日暂无待复习任务，请先生成复习任务")

    kp_ids = [t.knowledge_point_id for t in pending_tasks]
    kps = db.query(KnowledgePoint).filter(KnowledgePoint.id.in_(kp_ids)).all()

    if not kps:
        raise HTTPException(status_code=404, detail="复习任务关联的知识点不存在")

    return await _generate_collection_audio(db, kps, "每日复习音频", "daily_review")


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

    return await _generate_collection_audio(db, kps, "错题复习音频", "wrong_question")


@router.post("/retry/{audio_id}")
async def retry_audio(audio_id: int, db: Session = Depends(get_db)):
    audio_record = db.query(AudioFile).filter(AudioFile.id == audio_id).first()
    if not audio_record:
        raise HTTPException(status_code=404, detail="音频记录不存在")
    if audio_record.status != "failed":
        raise HTTPException(status_code=400, detail="只有失败状态的音频可以重新生成")

    config = _get_tts_config(db)
    filename = Path(audio_record.file_path or "").name
    current_ext = Path(filename).suffix.lower().lstrip(".")
    if not filename or "." not in filename or current_ext != config["audio_format"]:
        if audio_record.audio_type == "single":
            filename = generate_audio_filename(audio_record.knowledge_point_id, ext=config["audio_format"])
        else:
            filename = generate_collection_filename([audio_record.knowledge_point_id], ext=config["audio_format"])

    if audio_record.file_path:
        delete_audio_file(audio_record.file_path)

    audio_record.status = "pending"
    audio_record.error_message = None
    audio_record.provider = config["provider"]
    audio_record.voice = config["voice"]
    audio_record.audio_format = config["audio_format"]
    audio_record.file_url = build_file_url(filename)
    audio_record.file_path = filename
    audio_record.file_size = None
    db.commit()
    db.refresh(audio_record)

    audio_record = await _render_audio_record(db, audio_record, filename, config)
    return _audio_response(audio_record)
