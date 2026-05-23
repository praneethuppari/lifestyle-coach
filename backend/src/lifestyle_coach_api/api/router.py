from fastapi import APIRouter

from lifestyle_coach_api.api.routes.health import router as health_router
from lifestyle_coach_api.api.routes.recipes import router as recipes_router
from lifestyle_coach_api.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(users_router)
api_router.include_router(recipes_router)
