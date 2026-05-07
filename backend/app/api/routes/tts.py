import sys
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.config import (
    get_setting, TTS_PROVIDER,
    XIAOMI_TTS_API_KEY, XIAOMI_TTS_BASE_URL, XIAOMI_TTS_VOICE,
)
from ...models.knowledge_point import KnowledgePoint
from ...models.audio_file import AudioFile
from ...services.tts_service import build_text_from_knowledge_point, synthesize_audio
from ...services.audio_service import generate_audio_filename, save_audio_file, build_file_url

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

    # 根据 provider 决定文件格式
    audio_ext = "wav"
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

    # 获取 TTS 配置
    provider = TTS_PROVIDER
    xiaomi_key = XIAOMI_TTS_API_KEY
    xiaomi_base = XIAOMI_TTS_BASE_URL
    xiaomi_voice = XIAOMI_TTS_VOICE
    print(f"配置: provider={provider}, key={xiaomi_key[:10] if xiaomi_key else 'EMPTY'}..., base={xiaomi_base}", flush=True)

    try:
        print("开始调用 synthesize_audio...", flush=True)
        audio_bytes = await synthesize_audio(
            text_content,
            provider=provider,
            api_key=xiaomi_key,
            base_url=xiaomi_base,
            voice=xiaomi_voice,
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
