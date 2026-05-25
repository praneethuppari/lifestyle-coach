from fastapi import APIRouter

from lifestyle_coach_api.api.routes.auth import router as auth_router
from lifestyle_coach_api.api.routes.health import router as health_router
from lifestyle_coach_api.api.routes.ingredients import (
    catalog_router as ingredients_catalog_router,
    personal_router as ingredients_personal_router,
)
from lifestyle_coach_api.api.routes.recipes import (
    catalog_router,
    personal_router,
)
api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(personal_router)
api_router.include_router(catalog_router)
api_router.include_router(ingredients_personal_router)
api_router.include_router(ingredients_catalog_router)
