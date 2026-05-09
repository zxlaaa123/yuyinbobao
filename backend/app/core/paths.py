from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
UPLOAD_DIR = DATA_DIR / "uploads"
AUDIO_DIR = DATA_DIR / "audio"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
BACKUP_DIR = DATA_DIR / "backups"
