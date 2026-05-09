from collections.abc import Mapping, Sequence

from fastapi.responses import JSONResponse

from ..schemas.common import ErrorResponse


def normalize_error_detail(detail, fallback: str = "请求失败") -> str:
    if detail is None:
        return fallback

    if isinstance(detail, str):
        return detail.strip() or fallback

    if isinstance(detail, Mapping):
        for key in ("detail", "message", "error", "msg"):
            value = detail.get(key)
            if value:
                return normalize_error_detail(value, fallback)
        loc = detail.get("loc")
        msg = detail.get("msg")
        if msg:
            field = ".".join(str(item) for item in loc if item != "body") if isinstance(loc, Sequence) else ""
            return f"{field}：{msg}" if field else str(msg)
        return fallback

    if isinstance(detail, Sequence) and not isinstance(detail, (str, bytes, bytearray)):
        messages = [normalize_error_detail(item, "") for item in detail]
        messages = [item for item in messages if item]
        return "；".join(messages) if messages else fallback

    return str(detail) or fallback


def normalize_validation_errors(errors: list[dict]) -> str:
    field_messages = {
        "knowledge_base_id": "请选择知识库",
        "title": "资料标题不能为空",
        "content": "资料正文不能为空",
        "material_id": "缺少 material_id",
        "knowledge_point_id": "缺少 knowledge_point_id",
    }

    messages: list[str] = []
    for error in errors:
        loc = error.get("loc") or []
        field = str(loc[-1]) if loc else ""
        message = field_messages.get(field)
        if not message:
            message = normalize_error_detail(error, "")
        if message and message not in messages:
            messages.append(message)

    return "；".join(messages) if messages else "请求参数格式不正确"


def error_response(status_code: int, detail, code: str | None = None) -> JSONResponse:
    payload = ErrorResponse(
        detail=normalize_error_detail(detail),
        code=code,
    ).model_dump(exclude_none=True)
    return JSONResponse(status_code=status_code, content=payload)
