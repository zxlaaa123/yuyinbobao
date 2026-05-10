from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.paths import DATA_DIR, AUDIO_DIR, UPLOAD_DIR, VECTOR_STORE_DIR, BACKUP_DIR
from .core.config import get_cors_origins
from .core.database import engine, Base
from .core.errors import error_response, normalize_validation_errors
from .core.migrations import ensure_runtime_columns
from .core.startup import ensure_runtime_environment
from . import models
from .api import api_router

DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# 挂载静态文件目录
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(422, normalize_validation_errors(exc.errors()), code="VALIDATION_ERROR")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(500, "服务器内部错误，请稍后重试", code="INTERNAL_ERROR")


@app.on_event("startup")
def startup():
    ensure_runtime_environment(engine)
    Base.metadata.create_all(bind=engine)
    ensure_runtime_columns(engine)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app_name": "AI Study Cast",
        "version": "0.1.0",
    }
