import json
import re


def extract_json_from_text(text: str) -> dict:
    if not text:
        raise ValueError("AI 返回内容为空")

    # 1. 尝试直接解析纯 JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 2. 尝试提取 ```json ... ``` 代码块
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. 尝试截取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError("AI 返回结果不是有效 JSON，请重试")


def try_fix_json(text: str) -> str | None:
    """尝试修复常见 JSON 格式问题，返回修复后的文本或 None"""
    if not text:
        return None

    # 尝试提取 ```json ... ``` 代码块
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        candidate = match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            text = candidate

    # 尝试截取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    return None
