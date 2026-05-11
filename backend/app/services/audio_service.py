import time
import hashlib
from pathlib import Path
from ..core.paths import AUDIO_DIR


def generate_audio_filename(knowledge_point_id: int, ext: str = "wav") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    return f"kp_{knowledge_point_id}_{ts}.{ext}"


def generate_collection_filename(kp_ids: list[int], ext: str = "wav") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    ids_hash = hashlib.md5("_".join(str(i) for i in sorted(kp_ids)).encode()).hexdigest()[:12]
    return f"collection_{ids_hash}_{ts}.{ext}"


def save_audio_file(filename: str, content: bytes) -> str:
    filepath = AUDIO_DIR / filename
    with open(filepath, "wb") as f:
        f.write(content)
    return str(filepath)


def delete_audio_file(file_path: str) -> bool:
    try:
        audio_root = AUDIO_DIR.resolve()
        path = Path(file_path)
        if not path.is_absolute():
            path = AUDIO_DIR / path.name
        path = path.resolve()
        if not path.is_relative_to(audio_root):
            return False
        existed = path.exists()
        path.unlink(missing_ok=True)
        return existed
    except Exception:
        return False


def build_file_url(filename: str) -> str:
    return f"/audio/{filename}"
