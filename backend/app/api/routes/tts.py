from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.config import get_setting, TTS_PROVIDER
from ...models.knowledge_point import KnowledgePoint
from ...models.audio_file import AudioFile
from ...services.tts_service import build_text_from_knowledge_point, synthesize_audio
from ...services.audio_service import generate_audio_filename, save_audio_file, build_file_url

router = APIRouter(prefix="/api/tts", tags=["tts"])


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

    # 创建 audio_files 记录
    filename = generate_audio_filename(kp.id)
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

    # 获取 TTS Provider
    provider = get_setting(db, "TTS_PROVIDER", TTS_PROVIDER)

    try:
        # 调用 TTS 生成音频
        audio_bytes = await synthesize_audio(text_content, provider=provider)

        # 保存音频文件
        file_path = save_audio_file(filename, audio_bytes)

        # 更新记录
        audio_record.status = "success"
        audio_record.file_path = file_path
        db.commit()
        db.refresh(audio_record)

        return {
            "audio_id": audio_record.id,
            "knowledge_point_id": kp.id,
            "title": kp.title,
            "status": "success",
            "file_url": audio_record.file_url,
        }
    except Exception as e:
        audio_record.status = "failed"
        audio_record.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"TTS 生成失败：{str(e)}")
