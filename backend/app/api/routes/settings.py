import time

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.setting_service import get_all_settings, update_settings, mask_secret, SENSITIVE_KEYS
from ...services.ai_service import build_chat_completions_url
from ...services.ai_log_service import create_ai_call_log_independent

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
    prompt_text = "settings:test-ai:hi"
    started = time.perf_counter()

    if not api_key:
        message = "AI API Key 未配置，请先到设置页配置"
        _write_test_ai_log(
            status="failed",
            model=model,
            base_url=base_url,
            prompt_text=prompt_text,
            error_type="validation_error",
            error_message=message,
            duration_ms=_elapsed_ms(started),
        )
        return {"success": False, "message": message}
    if not base_url:
        message = "AI Base URL 未配置，请先到设置页配置"
        _write_test_ai_log(
            status="failed",
            model=model,
            base_url=base_url,
            prompt_text=prompt_text,
            error_type="validation_error",
            error_message=message,
            duration_ms=_elapsed_ms(started),
        )
        return {"success": False, "message": message}

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
                usage = None
                response_text = ""
                try:
                    data = resp.json()
                    usage = data.get("usage") if isinstance(data, dict) else None
                    if isinstance(data, dict):
                        choices = data.get("choices") or []
                        if choices and isinstance(choices[0], dict):
                            message = choices[0].get("message") or {}
                            response_text = str(message.get("content") or "")
                except Exception:
                    response_text = resp.text

                _write_test_ai_log(
                    status="success",
                    model=model,
                    base_url=base_url,
                    prompt_text=prompt_text,
                    response_text=response_text,
                    usage=usage,
                    duration_ms=_elapsed_ms(started),
                )
                return {"success": True, "message": "AI 连接正常", "model": model}
            else:
                message = f"AI 连接失败：HTTP {resp.status_code}"
                _write_test_ai_log(
                    status="failed",
                    model=model,
                    base_url=base_url,
                    prompt_text=prompt_text,
                    response_text=resp.text,
                    error_type="http_error",
                    http_status_code=resp.status_code,
                    error_message=message,
                    duration_ms=_elapsed_ms(started),
                )
                return {"success": False, "message": message}
    except httpx.TimeoutException:
        message = "AI 连接超时，请检查网络或 Base URL"
        _write_test_ai_log(
            status="failed",
            model=model,
            base_url=base_url,
            prompt_text=prompt_text,
            error_type="timeout",
            error_message=message,
            duration_ms=_elapsed_ms(started),
        )
        return {"success": False, "message": message}
    except Exception as e:
        message = f"AI 连接失败：{str(e)}"
        _write_test_ai_log(
            status="failed",
            model=model,
            base_url=base_url,
            prompt_text=prompt_text,
            error_type="unknown",
            error_message=message,
            duration_ms=_elapsed_ms(started),
        )
        return {"success": False, "message": message}


@router.post("/test-tts")
async def test_tts_connection(db: Session = Depends(get_db)):
    settings = get_all_settings(db)
    provider = settings.get("TTS_PROVIDER", "mock")

    if provider == "mock":
        return {"success": True, "message": "Mock TTS 可用（占位音频）"}

    if provider == "xiaomi":
        api_key = settings.get("XIAOMI_TTS_API_KEY", "")
        base_url = settings.get("XIAOMI_TTS_BASE_URL", "")
        model = settings.get("XIAOMI_TTS_MODEL", "mimo-v2.5-tts")
        voice = settings.get("XIAOMI_TTS_VOICE", "mimo_default")
        audio_format = settings.get("XIAOMI_TTS_FORMAT", "wav")
        style_prompt = settings.get("XIAOMI_TTS_STYLE_PROMPT", "用清晰、自然的语调朗读以下知识点内容，语速适中，发音标准。")
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
            "model": model,
            "messages": [
                {"role": "user", "content": style_prompt},
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


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _write_test_ai_log(
    *,
    status: str,
    model: str,
    base_url: str,
    prompt_text: str,
    response_text: str = "",
    usage: dict | None = None,
    error_type: str | None = None,
    error_message: str = "",
    http_status_code: int | None = None,
    duration_ms: int = 0,
) -> None:
    try:
        create_ai_call_log_independent(
            operation="test_ai_connection",
            model=model or "",
            base_url=base_url or "",
            status=status,
            prompt_text=prompt_text,
            response_text=response_text,
            usage=usage,
            error_type=error_type,
            error_message=error_message,
            json_parse_status="not_required",
            http_status_code=http_status_code,
            duration_ms=duration_ms,
            related_type="settings",
        )
    except Exception:
        pass
