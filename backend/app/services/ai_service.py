import httpx
from .json_parser import extract_json_from_text, try_fix_json
from .prompt_templates import (
    EXTRACT_KNOWLEDGE_POINTS_SYSTEM,
    GENERATE_QUESTIONS_SYSTEM,
    JSON_FIX_SYSTEM,
    build_extract_user_prompt,
    build_generate_questions_user_prompt,
    build_json_fix_prompt,
)


class AIService:
    def __init__(self, api_key: str, base_url: str, model: str, temperature: float = 0.3, timeout: int = 120):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def _build_chat_url(self) -> str:
        if self.base_url.endswith("/v1"):
            return f"{self.base_url}/chat/completions"
        return f"{self.base_url}/v1/chat/completions"

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self._build_chat_url(), json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def extract_knowledge_points(self, knowledge_base_name: str, material_title: str, material_content: str) -> dict:
        user_prompt = build_extract_user_prompt(knowledge_base_name, material_title, material_content)
        raw = await self.chat(EXTRACT_KNOWLEDGE_POINTS_SYSTEM, user_prompt)
        try:
            result = extract_json_from_text(raw)
        except ValueError:
            # JSON 解析失败，尝试修复一次
            fixed = try_fix_json(raw)
            if fixed:
                try:
                    result = extract_json_from_text(fixed)
                except ValueError:
                    raise ValueError("AI 返回结果不是有效 JSON，修复失败，请重试")
            else:
                # 用 AI 修复
                try:
                    fix_prompt = build_json_fix_prompt(raw[:3000])  # 限制长度
                    fixed_raw = await self.chat(JSON_FIX_SYSTEM, fix_prompt)
                    result = extract_json_from_text(fixed_raw)
                except Exception:
                    raise ValueError("AI 返回结果不是有效 JSON，修复失败，请重试")
        if "knowledge_points" not in result:
            raise ValueError("AI 返回结果缺少 knowledge_points 字段")
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
        raw = await self.chat(GENERATE_QUESTIONS_SYSTEM, user_prompt)
        try:
            result = extract_json_from_text(raw)
        except ValueError:
            # JSON 解析失败，尝试修复一次
            fixed = try_fix_json(raw)
            if fixed:
                try:
                    result = extract_json_from_text(fixed)
                except ValueError:
                    raise ValueError("AI 返回结果不是有效 JSON，修复失败，请重试")
            else:
                # 用 AI 修复
                try:
                    fix_prompt = build_json_fix_prompt(raw[:3000])
                    fixed_raw = await self.chat(JSON_FIX_SYSTEM, fix_prompt)
                    result = extract_json_from_text(fixed_raw)
                except Exception:
                    raise ValueError("AI 返回结果不是有效 JSON，修复失败，请重试")
        if "questions" not in result:
            raise ValueError("AI 返回结果缺少 questions 字段")
        return result
