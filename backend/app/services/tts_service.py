import json
import time
import httpx
import base64


def build_text_from_knowledge_points(kps: list) -> str:
    """多个知识点合集播报文本"""
    parts = []
    parts.append(f"接下来为您播放 {len(kps)} 个知识点的合集复习音频。")
    parts.append("")
    for i, kp in enumerate(kps, 1):
        parts.append(f"第 {i} 个知识点：{kp.title}。")
        if kp.summary:
            parts.append(f"简要解释：{kp.summary}")
        if kp.detail:
            parts.append(f"详细说明：{kp.detail}")
        if kp.exam_points:
            try:
                points = json.loads(kp.exam_points)
                if points:
                    parts.append("高频考点包括：")
                    for j, p in enumerate(points, 1):
                        parts.append(f"第{j}，{p}")
            except Exception:
                pass
        if kp.confusing_points:
            try:
                points = json.loads(kp.confusing_points)
                if points:
                    parts.append("易混点：")
                    for p in points:
                        parts.append(p)
            except Exception:
                pass
        if kp.memory_tips:
            try:
                tips = json.loads(kp.memory_tips)
                if tips:
                    parts.append("记忆方法：")
                    for t in tips:
                        parts.append(t)
            except Exception:
                pass
        if kp.examples:
            try:
                examples = json.loads(kp.examples)
                if examples:
                    parts.append("例子：")
                    for e in examples:
                        parts.append(e)
            except Exception:
                pass
        if i < len(kps):
            parts.append("")
            parts.append("接下来是第 {} 个知识点。".format(i + 1))
        parts.append("")
    parts.append("以上是本次合集复习的全部内容，请继续加油。")
    return "\n\n".join(parts)


def build_text_from_knowledge_point(kp) -> str:
    parts = []
    parts.append(f"知识点：{kp.title}。")
    if kp.summary:
        parts.append(f"简要解释：{kp.summary}")
    if kp.detail:
        parts.append(f"详细说明：{kp.detail}")
    if kp.exam_points:
        try:
            points = json.loads(kp.exam_points)
            if points:
                parts.append("高频考点包括：")
                for i, p in enumerate(points, 1):
                    parts.append(f"第{i}，{p}")
        except Exception:
            pass
    if kp.confusing_points:
        try:
            points = json.loads(kp.confusing_points)
            if points:
                parts.append("易混点：")
                for p in points:
                    parts.append(p)
        except Exception:
            pass
    if kp.memory_tips:
        try:
            tips = json.loads(kp.memory_tips)
            if tips:
                parts.append("记忆方法：")
                for t in tips:
                    parts.append(t)
        except Exception:
            pass
    if kp.examples:
        try:
            examples = json.loads(kp.examples)
            if examples:
                parts.append("例子：")
                for e in examples:
                    parts.append(e)
        except Exception:
            pass
    parts.append("本知识点播报结束。")
    return "\n\n".join(parts)


def normalize_audio_format(audio_format: str | None) -> str:
    normalized = (audio_format or "wav").strip().lower()
    if normalized not in {"wav", "pcm16"}:
        return "wav"
    return normalized


async def synthesize_audio(
    text: str,
    provider: str = "mock",
    api_key: str = "",
    base_url: str = "",
    model: str = "mimo-v2.5-tts",
    voice: str = "mimo_default",
    audio_format: str = "mp3",
    style_prompt: str = "",
) -> bytes:
    audio_format = normalize_audio_format(audio_format)
    if provider == "mock":
        return _mock_synthesize(text, audio_format)
    elif provider == "xiaomi":
        return await _xiaomi_synthesize(text, api_key, base_url, model, voice, audio_format, style_prompt)
    else:
        raise ValueError(f"不支持的 TTS Provider: {provider}")


def _mock_synthesize(text: str, audio_format: str) -> bytes:
    """Mock TTS：生成与配置格式一致的静音占位音频"""
    if audio_format == "wav":
        return _mock_wav(text)
    if audio_format == "pcm16":
        return b"\x00\x00" * _mock_sample_count(text)
    raise ValueError(f"不支持的音频格式: {audio_format}")


def _mock_sample_count(text: str) -> int:
    return min(max(8000, len(text) * 160), 8000 * 30)


def _mock_wav(text: str) -> bytes:
    import io
    import wave

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b"\x00\x00" * _mock_sample_count(text))
    return buffer.getvalue()


async def _xiaomi_synthesize(
    text: str,
    api_key: str,
    base_url: str,
    model: str,
    voice: str,
    audio_format: str,
    style_prompt: str,
) -> bytes:
    """小米 TTS Provider"""
    if not api_key:
        raise ValueError("小米 TTS API Key 未配置")
    if not base_url:
        raise ValueError("小米 TTS Base URL 未配置")

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": style_prompt
            },
            {
                "role": "assistant",
                "content": text
            }
        ],
        "audio": {
            "format": audio_format,
            "voice": voice
        },
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        raise ValueError(f"小米 TTS 接口调用失败：HTTP {exc.response.status_code}") from exc
    except httpx.TimeoutException as exc:
        raise ValueError("小米 TTS 接口调用超时") from exc

    # 解析音频数据
    try:
        audio_data = data["choices"][0]["message"]["audio"]["data"]
        return base64.b64decode(audio_data)
    except Exception as exc:
        raise ValueError("小米 TTS 返回音频数据格式异常") from exc
