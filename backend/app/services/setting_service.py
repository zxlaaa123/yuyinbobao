from sqlalchemy.orm import Session
from ..models.app_setting import AppSetting
from ..core.config import (
    AI_PROVIDER, AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_TEMPERATURE, AI_TIMEOUT,
    AI_SEGMENT_SIZE, AI_MAX_SEGMENTS,
    TTS_PROVIDER, XIAOMI_TTS_API_KEY, XIAOMI_TTS_BASE_URL, XIAOMI_TTS_VOICE,
    XIAOMI_TTS_FORMAT, XIAOMI_TTS_SPEED,
)

DEFAULTS = {
    "AI_PROVIDER": AI_PROVIDER,
    "AI_API_KEY": AI_API_KEY,
    "AI_BASE_URL": AI_BASE_URL,
    "AI_MODEL": AI_MODEL,
    "AI_TEMPERATURE": str(AI_TEMPERATURE),
    "AI_TIMEOUT": str(AI_TIMEOUT),
    "AI_SEGMENT_SIZE": str(AI_SEGMENT_SIZE),
    "AI_MAX_SEGMENTS": str(AI_MAX_SEGMENTS),
    "AI_INPUT_PRICE_PER_1M": "0",
    "AI_OUTPUT_PRICE_PER_1M": "0",
    "TTS_PROVIDER": TTS_PROVIDER,
    "XIAOMI_TTS_API_KEY": XIAOMI_TTS_API_KEY,
    "XIAOMI_TTS_BASE_URL": XIAOMI_TTS_BASE_URL,
    "XIAOMI_TTS_VOICE": XIAOMI_TTS_VOICE,
    "XIAOMI_TTS_FORMAT": XIAOMI_TTS_FORMAT,
    "XIAOMI_TTS_SPEED": str(XIAOMI_TTS_SPEED),
}

SENSITIVE_KEYS = {"AI_API_KEY", "XIAOMI_TTS_API_KEY"}


def get_all_settings(db: Session) -> dict:
    """读取所有配置，优先级：app_settings DB > .env > 默认值"""
    result = {}
    for key, default_val in DEFAULTS.items():
        record = db.query(AppSetting).filter(AppSetting.key == key).first()
        if record and record.value and record.value.strip():
            result[key] = record.value.strip()
        else:
            result[key] = default_val
    return result


def update_settings(db: Session, data: dict) -> dict:
    """更新配置，敏感字段传空时保留旧值"""
    for key, value in data.items():
        if key not in DEFAULTS:
            continue
        record = db.query(AppSetting).filter(AppSetting.key == key).first()
        if not record:
            record = AppSetting(key=key, is_secret=(key in SENSITIVE_KEYS))
            db.add(record)
        # 敏感字段传空时保留旧值
        if key in SENSITIVE_KEYS and (value is None or str(value).strip() == ""):
            continue
        record.value = str(value).strip()
    db.commit()
    return get_all_settings(db)


def mask_secret(value: str) -> str:
    """脱敏：sk-1234567890abcd → sk-1****abcd"""
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]
