def split_text(text: str, segment_size: int = 3000, max_segments: int = 5) -> list[str]:
    """
    将长文本按段落边界分段。
    优先在段落分隔处（空行）切割，其次在句子边界（句号/问号/感叹号）切割。
    每段不超过 segment_size 字符，总段数不超过 max_segments。
    """
    segment_size = max(segment_size, 100)
    max_segments = max(max_segments, 1)
    if len(text) <= segment_size:
        return [text]

    segments = []
    remaining = text

    while remaining and len(segments) < max_segments:
        if len(remaining) <= segment_size:
            segments.append(remaining)
            break

        # 在 segment_size 范围内找最佳切割点
        cut_area = remaining[:segment_size]

        # 优先：空行（段落边界）
        last_para = cut_area.rfind("\n\n")
        if last_para > segment_size * 0.3:  # 至少保留 30% 内容
            cut_pos = last_para
        else:
            # 次选：句子边界
            for sep in ["。", "？", "！", ".", "?", "!"]:
                last_sep = cut_area.rfind(sep)
                if last_sep > segment_size * 0.3:
                    cut_pos = last_sep + 1
                    break
            else:
                # 兜回：硬切
                cut_pos = segment_size

        segments.append(remaining[:cut_pos].strip())
        remaining = remaining[cut_pos:].strip()

    # 如果还有剩余，追加到最后一段（可能超长，但保证内容不丢）
    if remaining and len(segments) >= max_segments:
        segments[-1] += "\n\n" + remaining

    return segments
