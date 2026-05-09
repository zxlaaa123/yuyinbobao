from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.ai_call_log import AICallLog

router = APIRouter(prefix="/api/ai-call-logs", tags=["ai-call-logs"])


@router.get("")
def list_ai_call_logs(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    operation: str | None = None,
    error_type: str | None = None,
    json_parse_status: str | None = None,
    db: Session = Depends(get_db),
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    query = db.query(AICallLog)
    if status:
        query = query.filter(AICallLog.status == status)
    if operation:
        query = query.filter(AICallLog.operation == operation)
    if error_type:
        query = query.filter(AICallLog.error_type == error_type)
    if json_parse_status:
        query = query.filter(AICallLog.json_parse_status == json_parse_status)

    total = query.count()
    logs = query.order_by(AICallLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [_to_response(item) for item in logs],
    }


@router.get("/summary")
def get_ai_call_log_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(AICallLog.id)).scalar() or 0
    success = db.query(func.count(AICallLog.id)).filter(AICallLog.status == "success").scalar() or 0
    failed = db.query(func.count(AICallLog.id)).filter(AICallLog.status == "failed").scalar() or 0
    token_sum = db.query(func.coalesce(func.sum(AICallLog.total_tokens), 0)).scalar() or 0
    cost_sum = db.query(func.coalesce(func.sum(AICallLog.estimated_cost), 0)).scalar() or 0
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "total_tokens": int(token_sum),
        "estimated_cost": float(cost_sum),
    }


@router.get("/{log_id}")
def get_ai_call_log(log_id: int, db: Session = Depends(get_db)):
    item = db.query(AICallLog).filter(AICallLog.id == log_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="AI 日志不存在")
    return _to_response(item)


@router.delete("/{log_id}")
def delete_ai_call_log(log_id: int, db: Session = Depends(get_db)):
    item = db.query(AICallLog).filter(AICallLog.id == log_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="AI 日志不存在")
    db.delete(item)
    db.commit()
    return {"success": True, "message": "AI 日志已删除"}


def _to_response(item: AICallLog) -> dict:
    return {
        "id": item.id,
        "operation": item.operation,
        "model": item.model,
        "base_url_host": item.base_url_host,
        "status": item.status,
        "prompt_chars": item.prompt_chars,
        "response_chars": item.response_chars,
        "prompt_tokens": item.prompt_tokens,
        "completion_tokens": item.completion_tokens,
        "total_tokens": item.total_tokens,
        "tokens_estimated": item.tokens_estimated,
        "estimated_cost": item.estimated_cost,
        "input_price_per_1m": item.input_price_per_1m,
        "output_price_per_1m": item.output_price_per_1m,
        "duration_ms": item.duration_ms,
        "request_summary": item.request_summary,
        "response_summary": item.response_summary,
        "error_type": item.error_type,
        "error_message": item.error_message,
        "json_parse_status": item.json_parse_status,
        "http_status_code": item.http_status_code,
        "related_type": item.related_type,
        "related_id": item.related_id,
        "created_at": item.created_at,
    }
