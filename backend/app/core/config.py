from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_setting(db, key: str, default: str = "") -> str:
    from ..models.app_setting import AppSetting
    record = db.query(AppSetting).filter(AppSetting.key == key).first()
    if record and record.value:
        return record.value
    return os.getenv(key, default)


AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))
