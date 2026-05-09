import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.setting_service import get_all_settings, update_settings, mask_secret, SENSITIVE_KEYS
from ...services.ai_service import build_chat_completions_url

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db)):
    settings = get_all_settings(db)
    # 敏感字段脱敏
    for key in SENSITIVE_KEYS:
        if key in settings and settings[key]:
            settings[key] = mask_secret(settings[key])
    return settings


@router.put("")
def put_settings(body: dict, db: Session = Depends(get_db)):
    updated = update_settings(db, body)
    # 敏感字段脱敏后返回
    for key in SENSITIVE_KEYS:
        if key in updated and updated[key]:
            updated[key] = mask_secret(updated[key])
    return {"success": True, "message": "设置已保存", "settings": updated}


@router.post("/test-ai")
async def test_ai_connection(db: Session = Depends(get_db)):
    settings = get_all_settings(db)
    api_key = settings.get("AI_API_KEY", "")
    base_url = settings.get("AI_BASE_URL", "")
    model = settings.get("AI_MODEL", "")

    if not api_key:
        return {"success": False, "message": "AI API Key 未配置，请先到设置页配置"}
    if not base_url:
        return {"success": False, "message": "AI Base URL 未配置，请先到设置页配置"}

    # 发送最小请求测试连通性
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                build_chat_completions_url(base_url),
                json=payload,
                headers=headers,
            )
            if resp.status_code == 200:
                return {"success": True, "message": "AI 连接正常", "model": model}
            else:
                return {"success": False, "message": f"AI 连接失败：HTTP {resp.status_code}"}
    except httpx.TimeoutException:
        return {"success": False, "message": "AI 连接超时，请检查网络或 Base URL"}
    except Exception as e:
        return {"success": False, "message": f"AI 连接失败：{str(e)}"}


@router.post("/test-tts")
async def test_tts_connection(db: Session = Depends(get_db)):
    settings = get_all_settings(db)
    provider = settings.get("TTS_PROVIDER", "mock")

    if provider == "mock":
        return {"success": True, "message": "Mock TTS 可用（占位音频）"}

    if provider == "xiaomi":
        api_key = settings.get("XIAOMI_TTS_API_KEY", "")
        base_url = settings.get("XIAOMI_TTS_BASE_URL", "")
        voice = settings.get("XIAOMI_TTS_VOICE", "mimo_default")
        audio_format = settings.get("XIAOMI_TTS_FORMAT", "mp3")
        if not api_key:
            return {"success": False, "message": "小米 TTS API Key 未配置，请先到设置页配置"}
        if not base_url:
            return {"success": False, "message": "小米 TTS Base URL 未配置，请先到设置页配置"}

        # 发送最小 TTS 请求测试
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "model": "mimo-v2.5-tts",
            "messages": [
                {"role": "user", "content": "用清晰自然的语调朗读。"},
                {"role": "assistant", "content": "测试音频。"}
            ],
            "audio": {"format": audio_format, "voice": voice},
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if "choices" in data and data["choices"]:
                        return {"success": True, "message": "小米 TTS 连接正常"}
                    return {"success": False, "message": "小米 TTS 返回格式异常"}
                else:
                    return {"success": False, "message": f"小米 TTS 连接失败：HTTP {resp.status_code}"}
        except httpx.TimeoutException:
            return {"success": False, "message": "小米 TTS 连接超时，请检查网络或 Base URL"}
        except Exception as e:
            return {"success": False, "message": f"小米 TTS 连接失败：{str(e)}"}

    return {"success": False, "message": f"不支持的 TTS Provider: {provider}"}
