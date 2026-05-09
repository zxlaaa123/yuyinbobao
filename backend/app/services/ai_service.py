import time

import httpx
from sqlalchemy.orm import Session

from .json_parser import extract_json_from_text, try_fix_json
from .ai_log_service import create_ai_call_log_independent
from .prompt_templates import (
    EXTRACT_KNOWLEDGE_POINTS_SYSTEM,
    GENERATE_QUESTIONS_SYSTEM,
    JSON_FIX_SYSTEM,
    build_extract_user_prompt,
    build_generate_questions_user_prompt,
    build_json_fix_prompt,
)


def build_chat_completions_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/v1"):
        return f"{normalized}/chat/completions"
    return f"{normalized}/v1/chat/completions"


class AIService:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.3,
        timeout: int = 120,
        db: Session | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.db = db

    def _build_chat_url(self) -> str:
        return build_chat_completions_url(self.base_url)

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        operation: str = "chat",
        related_type: str | None = None,
        related_id: int | None = None,
        log_call: bool = True,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
        }
        started = time.perf_counter()
        response_text = ""
        usage = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self._build_chat_url(), json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                usage = data.get("usage")
                response_text = data["choices"][0]["message"]["content"]
                return response_text
        except httpx.HTTPStatusError as exc:
            if log_call:
                self._write_log(
                    operation=operation,
                    status="failed",
                    prompt_text=user_prompt,
                    response_text=response_text,
                    error_type="http_error",
                    http_status_code=exc.response.status_code if exc.response else None,
                    error_message=str(exc),
                    duration_ms=_elapsed_ms(started),
                    usage=usage,
                    related_type=related_type,
                    related_id=related_id,
                )
            raise
        except httpx.TimeoutException as exc:
            if log_call:
                self._write_log(
                    operation=operation,
                    status="failed",
                    prompt_text=user_prompt,
                    response_text=response_text,
                    error_type="timeout",
                    error_message=str(exc),
                    duration_ms=_elapsed_ms(started),
                    usage=usage,
                    related_type=related_type,
                    related_id=related_id,
                )
            raise
        except Exception as exc:
            error_type, http_status_code = _classify_error(exc)
            if log_call:
                self._write_log(
                    operation=operation,
                    status="failed",
                    prompt_text=user_prompt,
                    response_text=response_text,
                    error_type=error_type,
                    http_status_code=http_status_code,
                    error_message=str(exc),
                    duration_ms=_elapsed_ms(started),
                    usage=usage,
                    related_type=related_type,
                    related_id=related_id,
                )
            raise
        finally:
            if log_call and response_text:
                self._write_log(
                    operation=operation,
                    status="success",
                    prompt_text=user_prompt,
                    response_text=response_text,
                    duration_ms=_elapsed_ms(started),
                    usage=usage,
                    related_type=related_type,
                    related_id=related_id,
                )

    async def extract_knowledge_points(
        self,
        knowledge_base_name: str,
        material_title: str,
        material_content: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> dict:
        user_prompt = build_extract_user_prompt(knowledge_base_name, material_title, material_content)
        started = time.perf_counter()
        raw = ""
        json_parse_status = "not_required"
        try:
            raw = await self.chat(EXTRACT_KNOWLEDGE_POINTS_SYSTEM, user_prompt, log_call=False)
            result = extract_json_from_text(raw)
            json_parse_status = "success"
        except ValueError as exc:
            # JSON 解析失败，尝试修复一次
            try:
                fixed = try_fix_json(raw)
                if fixed:
                    result = extract_json_from_text(fixed)
                    json_parse_status = "fixed"
                else:
                    # 用 AI 修复
                    fix_prompt = build_json_fix_prompt(raw[:3000])  # 限制长度
                    fixed_raw = await self.chat(JSON_FIX_SYSTEM, fix_prompt, operation="fix_json")
                    result = extract_json_from_text(fixed_raw)
                    json_parse_status = "fixed"
            except Exception:
                error = "AI 返回结果不是有效 JSON，修复失败，请重试"
                self._write_log(
                    operation="extract_knowledge_points",
                    status="failed",
                    prompt_text=user_prompt,
                    response_text=raw,
                    error_type="json_parse_error",
                    json_parse_status="failed",
                    error_message=f"{error}；原始错误：{str(exc)}",
                    duration_ms=_elapsed_ms(started),
                    related_type=related_type,
                    related_id=related_id,
                )
                raise ValueError(error)
        except Exception as exc:
            error_type, http_status_code = _classify_error(exc)
            self._write_log(
                operation="extract_knowledge_points",
                status="failed",
                prompt_text=user_prompt,
                response_text=raw,
                error_type=error_type,
                http_status_code=http_status_code,
                error_message=str(exc),
                json_parse_status="not_required",
                duration_ms=_elapsed_ms(started),
                related_type=related_type,
                related_id=related_id,
            )
            raise
        if "knowledge_points" not in result:
            error = "AI 返回结果缺少 knowledge_points 字段"
            self._write_log(
                operation="extract_knowledge_points",
                status="failed",
                prompt_text=user_prompt,
                response_text=raw,
                error_type="validation_error",
                json_parse_status=json_parse_status,
                error_message=error,
                duration_ms=_elapsed_ms(started),
                related_type=related_type,
                related_id=related_id,
            )
            raise ValueError(error)
        self._write_log(
            operation="extract_knowledge_points",
            status="success",
            prompt_text=user_prompt,
            response_text=raw,
            json_parse_status=json_parse_status,
            duration_ms=_elapsed_ms(started),
            related_type=related_type,
            related_id=related_id,
        )
        return result

    async def generate_questions(
        self,
        title: str,
        summary: str,
        detail: str,
        exam_points: list[str],
        confusing_points: list[str],
        memory_tips: list[str],
        examples: list[str],
        question_types: list[str],
        count: int,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> dict:
        user_prompt = build_generate_questions_user_prompt(
            title=title,
            summary=summary,
            detail=detail,
            exam_points=exam_points,
            confusing_points=confusing_points,
            memory_tips=memory_tips,
            examples=examples,
            question_types=question_types,
            count=count,
        )
        started = time.perf_counter()
        raw = ""
        json_parse_status = "not_required"
        try:
            raw = await self.chat(GENERATE_QUESTIONS_SYSTEM, user_prompt, log_call=False)
            result = extract_json_from_text(raw)
            json_parse_status = "success"
        except ValueError as exc:
            # JSON 解析失败，尝试修复一次
            try:
                fixed = try_fix_json(raw)
                if fixed:
                    result = extract_json_from_text(fixed)
                    json_parse_status = "fixed"
                else:
                    # 用 AI 修复
                    fix_prompt = build_json_fix_prompt(raw[:3000])
                    fixed_raw = await self.chat(JSON_FIX_SYSTEM, fix_prompt, operation="fix_json")
                    result = extract_json_from_text(fixed_raw)
                    json_parse_status = "fixed"
            except Exception:
                error = "AI 返回结果不是有效 JSON，修复失败，请重试"
                self._write_log(
                    operation="generate_questions",
                    status="failed",
                    prompt_text=user_prompt,
                    response_text=raw,
                    error_type="json_parse_error",
                    json_parse_status="failed",
                    error_message=f"{error}；原始错误：{str(exc)}",
                    duration_ms=_elapsed_ms(started),
                    related_type=related_type,
                    related_id=related_id,
                )
                raise ValueError(error)
        except Exception as exc:
            error_type, http_status_code = _classify_error(exc)
            self._write_log(
                operation="generate_questions",
                status="failed",
                prompt_text=user_prompt,
                response_text=raw,
                error_type=error_type,
                http_status_code=http_status_code,
                error_message=str(exc),
                json_parse_status="not_required",
                duration_ms=_elapsed_ms(started),
                related_type=related_type,
                related_id=related_id,
            )
            raise
        if "questions" not in result:
            error = "AI 返回结果缺少 questions 字段"
            self._write_log(
                operation="generate_questions",
                status="failed",
                prompt_text=user_prompt,
                response_text=raw,
                error_type="validation_error",
                json_parse_status=json_parse_status,
                error_message=error,
                duration_ms=_elapsed_ms(started),
                related_type=related_type,
                related_id=related_id,
            )
            raise ValueError(error)
        self._write_log(
            operation="generate_questions",
            status="success",
            prompt_text=user_prompt,
            response_text=raw,
            json_parse_status=json_parse_status,
            duration_ms=_elapsed_ms(started),
            related_type=related_type,
            related_id=related_id,
        )
        return result

    def _write_log(
        self,
        *,
        operation: str,
        status: str,
        prompt_text: str,
        response_text: str = "",
        error_type: str | None = None,
        error_message: str = "",
        json_parse_status: str = "not_required",
        http_status_code: int | None = None,
        duration_ms: int = 0,
        usage: dict | None = None,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> None:
        if not self.db:
            return
        try:
            create_ai_call_log_independent(
                operation=operation,
                model=self.model,
                base_url=self.base_url,
                status=status,
                prompt_text=prompt_text,
                response_text=response_text,
                error_type=error_type,
                error_message=error_message,
                json_parse_status=json_parse_status,
                http_status_code=http_status_code,
                duration_ms=duration_ms,
                usage=usage,
                related_type=related_type,
                related_id=related_id,
            )
        except Exception:
            pass


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _classify_error(exc: Exception) -> tuple[str, int | None]:
    if isinstance(exc, httpx.TimeoutException):
        return "timeout", None
    if isinstance(exc, httpx.HTTPStatusError):
        return "http_error", exc.response.status_code if exc.response else None
    if isinstance(exc, ValueError):
        return "validation_error", None
    return "unknown", None
