import time
import httpx
import base64
from .audio_service import generate_audio_filename, save_audio_file, build_file_url


def build_text_from_knowledge_point(kp) -> str:
    parts = []
    parts.append(f"知识点：{kp.title}。")
    if kp.summary:
        parts.append(f"简要解释：{kp.summary}")
    if kp.detail:
        parts.append(f"详细说明：{kp.detail}")
    if kp.exam_points:
        import json
        try:
            points = json.loads(kp.exam_points)
            if points:
                parts.append("高频考点包括：")
                for i, p in enumerate(points, 1):
                    parts.append(f"第{i}，{p}")
        except Exception:
            pass
    if kp.confusing_points:
        import json
        try:
            points = json.loads(kp.confusing_points)
            if points:
                parts.append("易混点：")
                for p in points:
                    parts.append(p)
        except Exception:
            pass
    if kp.memory_tips:
        import json
        try:
            tips = json.loads(kp.memory_tips)
            if tips:
                parts.append("记忆方法：")
                for t in tips:
                    parts.append(t)
        except Exception:
            pass
    if kp.examples:
        import json
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


async def synthesize_audio(text: str, provider: str = "mock", api_key: str = "", base_url: str = "", voice: str = "mimo_default") -> bytes:
    if provider == "mock":
        return _mock_synthesize(text)
    elif provider == "xiaomi":
        return await _xiaomi_synthesize(text, api_key, base_url, voice)
    else:
        raise ValueError(f"不支持的 TTS Provider: {provider}")


def _mock_synthesize(text: str) -> bytes:
    """Mock TTS：生成一个简短的静音 MP3 占位文件"""
    mp3_header = b'\xff\xfb\x90\x00'
    silent_frame = mp3_header + b'\x00' * 417
    num_frames = max(1, len(text) // 50)
    return silent_frame * min(num_frames, 30)


async def _xiaomi_synthesize(text: str, api_key: str, base_url: str, voice: str) -> bytes:
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
        "model": "mimo-v2.5-tts",
        "messages": [
            {
                "role": "user",
                "content": "用清晰、自然的语调朗读以下知识点内容，语速适中，发音标准。"
            },
            {
                "role": "assistant",
                "content": text
            }
        ],
        "audio": {
            "format": "wav",
            "voice": voice
        }
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # 解析音频数据
    audio_data = data["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_data)
