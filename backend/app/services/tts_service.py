import time
from .audio_service import generate_audio_filename, save_audio_file, build_file_url
from .prompt_templates import build_extract_user_prompt


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


async def synthesize_audio(text: str, provider: str = "mock") -> bytes:
    if provider == "mock":
        return _mock_synthesize(text)
    elif provider == "xiaomi":
        return await _xiaomi_synthesize(text)
    else:
        raise ValueError(f"不支持的 TTS Provider: {provider}")


def _mock_synthesize(text: str) -> bytes:
    """Mock TTS：生成一个简短的静音 MP3 占位文件"""
    # 生成一个最小的有效 MP3 文件（静音）
    import struct
    # MP3 文件头 + 静音帧
    mp3_header = b'\xff\xfb\x90\x00'
    # 生成约 1 秒的静音 MP3 数据
    silent_frame = mp3_header + b'\x00' * 417
    num_frames = max(1, len(text) // 50)  # 根据文本长度决定"时长"
    return silent_frame * min(num_frames, 30)  # 最多 30 帧


async def _xiaomi_synthesize(text: str) -> bytes:
    """小米 TTS Provider（预留）"""
    raise NotImplementedError("小米 TTS Provider 尚未实现，请配置 XIAOMI_TTS_API_KEY 和 XIAOMI_TTS_BASE_URL")
