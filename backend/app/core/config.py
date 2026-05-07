from pathlib import Path
import os


def _load_env():
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_env()


def get_setting(db, key: str, default: str = "") -> str:
    from ..models.app_setting import AppSetting
    record = db.query(AppSetting).filter(AppSetting.key == key).first()
    if record and record.value and record.value.strip():
        return record.value.strip()
    val = os.getenv(key, "")
    return val if val else default


AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "mock")
XIAOMI_TTS_API_KEY = os.getenv("XIAOMI_TTS_API_KEY", "")
XIAOMI_TTS_BASE_URL = os.getenv("XIAOMI_TTS_BASE_URL", "")
XIAOMI_TTS_VOICE = os.getenv("XIAOMI_TTS_VOICE", "mimo_default")
