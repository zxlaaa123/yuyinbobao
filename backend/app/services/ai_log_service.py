from urllib.parse import urlparse

from sqlalchemy.orm import Session

from ..core.config import get_setting
from ..core.database import SessionLocal
from ..models.ai_call_log import AICallLog


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, round(len(text) / 4))


def estimate_cost(prompt_tokens: int, completion_tokens: int, input_price: float, output_price: float) -> float:
    return round((prompt_tokens / 1_000_000 * input_price) + (completion_tokens / 1_000_000 * output_price), 8)


def get_ai_price_settings(db: Session) -> tuple[float, float]:
    input_price = _to_float(get_setting(db, "AI_INPUT_PRICE_PER_1M", "0"), 0)
    output_price = _to_float(get_setting(db, "AI_OUTPUT_PRICE_PER_1M", "0"), 0)
    return input_price, output_price


def create_ai_call_log(
    db: Session,
    *,
    operation: str,
    model: str,
    base_url: str,
    status: str,
    prompt_text: str,
    response_text: str = "",
    error_message: str = "",
    duration_ms: int = 0,
    usage: dict | None = None,
    related_type: str | None = None,
    related_id: int | None = None,
) -> AICallLog:
    usage = usage or {}
    prompt_chars = len(prompt_text or "")
    response_chars = len(response_text or "")

    prompt_tokens = _to_int(usage.get("prompt_tokens"), 0)
    completion_tokens = _to_int(usage.get("completion_tokens"), 0)
    total_tokens = _to_int(usage.get("total_tokens"), 0)
    tokens_estimated = False

    if prompt_tokens <= 0:
        prompt_tokens = estimate_tokens(prompt_text)
        tokens_estimated = True
    if completion_tokens <= 0:
        completion_tokens = estimate_tokens(response_text)
        tokens_estimated = True
    if total_tokens <= 0:
        total_tokens = prompt_tokens + completion_tokens

    input_price, output_price = get_ai_price_settings(db)
    log = AICallLog(
        operation=operation,
        model=model,
        base_url_host=_host_only(base_url),
        status=status,
        prompt_chars=prompt_chars,
        response_chars=response_chars,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        tokens_estimated=tokens_estimated,
        estimated_cost=estimate_cost(prompt_tokens, completion_tokens, input_price, output_price),
        input_price_per_1m=input_price,
        output_price_per_1m=output_price,
        duration_ms=duration_ms,
        request_summary=_summary(prompt_text),
        response_summary=_summary(response_text),
        error_message=_summary(error_message, 500),
        related_type=related_type,
        related_id=related_id,
    )
    db.add(log)
    db.flush()
    db.refresh(log)
    return log


def create_ai_call_log_independent(**kwargs) -> None:
    db = SessionLocal()
    try:
        create_ai_call_log(db, **kwargs)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _summary(text: str | None, limit: int = 500) -> str:
    cleaned = " ".join((text or "").split())
    return cleaned[:limit]


def _host_only(url: str) -> str:
    parsed = urlparse(url or "")
    return parsed.netloc or parsed.path[:200]


def _to_int(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _to_float(value, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback
