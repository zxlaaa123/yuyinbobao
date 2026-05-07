from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.paths import DATA_DIR, AUDIO_DIR, UPLOAD_DIR, VECTOR_STORE_DIR
from .core.database import engine, Base
from . import models
from .api import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# 挂载静态文件目录
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")


@app.on_event("startup")
def startup():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app_name": "AI Study Cast",
        "version": "0.1.0",
    }
