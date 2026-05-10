import ast
import json
import re
from typing import Any, Iterable


_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*([\s\S]*?)\s*```")
_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def extract_json_from_text(text: str) -> Any:
    if not text:
        raise ValueError("AI 返回内容为空")

    for candidate in _iter_candidates(text):
        parsed = _loads(candidate)
        if parsed is not None:
            return parsed

    raise ValueError("AI 返回结果不是有效 JSON，请重试")


def try_fix_json(text: str) -> str | None:
    if not text:
        return None

    for candidate in _iter_candidates(text):
        parsed = _loads(candidate)
        if parsed is not None:
            return json.dumps(parsed, ensure_ascii=False)

    return None


def _iter_candidates(text: str) -> Iterable[str]:
    cleaned = _strip_bom(text).strip()
    if not cleaned:
        return

    yield cleaned

    for match in _FENCE_RE.finditer(cleaned):
      yield match.group(1).strip()

    for candidate in _balanced_json_candidates(cleaned):
        yield candidate

    repaired = _repair_json_text(cleaned)
    if repaired != cleaned:
        yield repaired
        for candidate in _balanced_json_candidates(repaired):
            yield candidate


def _loads(candidate: str) -> Any | None:
    candidate = candidate.strip()
    if not candidate:
        return None

    for item in (candidate, _repair_json_text(candidate)):
        try:
            return json.loads(item)
        except json.JSONDecodeError:
            pass

    try:
        value = ast.literal_eval(candidate)
    except (ValueError, SyntaxError):
        return None

    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return None
    return value


def _strip_bom(text: str) -> str:
    return text.lstrip("\ufeff").strip()


def _repair_json_text(text: str) -> str:
    text = _strip_bom(text)
    text = _remove_json_comments(text)
    return _TRAILING_COMMA_RE.sub(r"\1", text).strip()


def _remove_json_comments(text: str) -> str:
    result: list[str] = []
    in_string = False
    quote = ""
    escaped = False
    i = 0

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_string:
            result.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                in_string = False
            i += 1
            continue

        if ch in ('"', "'"):
            in_string = True
            quote = ch
            result.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            continue

        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue

        result.append(ch)
        i += 1

    return "".join(result)


def _balanced_json_candidates(text: str) -> Iterable[str]:
    pairs = {"{": "}", "[": "]"}

    for start, open_ch in enumerate(text):
        if open_ch not in pairs:
            continue
        expected_stack = [pairs[open_ch]]
        in_string = False
        quote = ""
        escaped = False

        for index in range(start + 1, len(text)):
            ch = text[index]

            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == quote:
                    in_string = False
                continue

            if ch in ('"', "'"):
                in_string = True
                quote = ch
                continue

            if ch in pairs:
                expected_stack.append(pairs[ch])
                continue

            if expected_stack and ch == expected_stack[-1]:
                expected_stack.pop()
                if not expected_stack:
                    yield text[start:index + 1]
                    break
