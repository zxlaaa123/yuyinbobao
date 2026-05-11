from pathlib import Path
import os
from dotenv import load_dotenv


def _load_env():
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)


_load_env()


def get_setting(db, key: str, default: str = "") -> str:
    from ..models.app_setting import AppSetting
    record = db.query(AppSetting).filter(AppSetting.key == key).first()
    if record and record.value and record.value.strip():
        return record.value.strip()
    val = os.getenv(key, "")
    return val if val else default


def _get_int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_float_env(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS") or os.getenv("FRONTEND_URL", "http://localhost:5173")
    origins = [item.strip().rstrip("/") for item in raw.split(",") if item.strip()]
    defaults = ["http://localhost:5173", "http://127.0.0.1:5173"]
    for origin in defaults:
        if origin not in origins:
            origins.append(origin)
    return origins


AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
AI_TEMPERATURE = _get_float_env("AI_TEMPERATURE", 0.3)
AI_TIMEOUT = _get_int_env("AI_TIMEOUT", 120)
AI_SEGMENT_SIZE = _get_int_env("AI_SEGMENT_SIZE", 3000)
AI_MAX_SEGMENTS = _get_int_env("AI_MAX_SEGMENTS", 5)
MAX_UPLOAD_SIZE_MB = _get_int_env("MAX_UPLOAD_SIZE_MB", 10)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "mock")
XIAOMI_TTS_API_KEY = os.getenv("XIAOMI_TTS_API_KEY", "")
XIAOMI_TTS_BASE_URL = os.getenv("XIAOMI_TTS_BASE_URL", "")
XIAOMI_TTS_MODEL = os.getenv("XIAOMI_TTS_MODEL", "mimo-v2.5-tts")
XIAOMI_TTS_VOICE = os.getenv("XIAOMI_TTS_VOICE", "mimo_default")
XIAOMI_TTS_FORMAT = os.getenv("XIAOMI_TTS_FORMAT", "wav")
XIAOMI_TTS_SPEED = _get_float_env("XIAOMI_TTS_SPEED", 1.0)
XIAOMI_TTS_STYLE_PROMPT = os.getenv(
    "XIAOMI_TTS_STYLE_PROMPT",
    "用清晰、自然的语调朗读以下知识点内容，语速适中，发音标准。",
)
