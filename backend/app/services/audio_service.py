import time
from pathlib import Path
from ..core.paths import AUDIO_DIR


def generate_audio_filename(knowledge_point_id: int, ext: str = "wav") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    return f"kp_{knowledge_point_id}_{ts}.{ext}"


def generate_collection_filename(kp_ids: list[int], ext: str = "wav") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    ids_hash = "_".join(str(i) for i in sorted(kp_ids))
    return f"collection_{ids_hash}_{ts}.{ext}"


def save_audio_file(filename: str, content: bytes) -> str:
    filepath = AUDIO_DIR / filename
    with open(filepath, "wb") as f:
        f.write(content)
    return str(filepath)


def delete_audio_file(file_path: str) -> bool:
    try:
        Path(file_path).unlink(missing_ok=True)
        return True
    except Exception:
        return False


def build_file_url(filename: str) -> str:
    return f"/audio/{filename}"
