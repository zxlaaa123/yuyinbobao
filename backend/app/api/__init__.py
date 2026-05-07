from fastapi import APIRouter
from .routes.knowledge_bases import router as knowledge_bases_router
from .routes.materials import router as materials_router
from .routes.ai import router as ai_router

api_router = APIRouter()
api_router.include_router(knowledge_bases_router)
api_router.include_router(materials_router)
api_router.include_router(ai_router)
