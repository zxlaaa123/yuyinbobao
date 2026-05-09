from fastapi import APIRouter
from .routes.knowledge_bases import router as knowledge_bases_router
from .routes.materials import router as materials_router
from .routes.ai import router as ai_router
from .routes.knowledge_points import router as knowledge_points_router
from .routes.questions import router as questions_router
from .routes.practice import router as practice_router
from .routes.wrong_questions import router as wrong_questions_router
from .routes.tts import router as tts_router
from .routes.audio_files import router as audio_files_router
from .routes.settings import router as settings_router
from .routes.dashboard import router as dashboard_router
from .routes.stats import router as stats_router
from .routes.review import router as review_router
from .routes.flashcards import router as flashcards_router
from .routes.export import router as export_router
from .routes.backups import router as backups_router
from .routes.study_sessions import router as study_sessions_router
from .routes.ai_call_logs import router as ai_call_logs_router
from .routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(knowledge_bases_router)
api_router.include_router(materials_router)
api_router.include_router(ai_router)
api_router.include_router(knowledge_points_router)
api_router.include_router(questions_router)
api_router.include_router(practice_router)
api_router.include_router(wrong_questions_router)
api_router.include_router(tts_router)
api_router.include_router(audio_files_router)
api_router.include_router(settings_router)
api_router.include_router(dashboard_router)
api_router.include_router(stats_router)
api_router.include_router(review_router)
api_router.include_router(flashcards_router)
api_router.include_router(export_router)
api_router.include_router(backups_router)
api_router.include_router(study_sessions_router)
api_router.include_router(ai_call_logs_router)
api_router.include_router(search_router)
