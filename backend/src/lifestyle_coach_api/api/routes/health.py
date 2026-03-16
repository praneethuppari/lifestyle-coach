from typing import Annotated

from fastapi import APIRouter, Depends

from lifestyle_coach_api.core.config import Settings, get_settings
from lifestyle_coach_api.schemas.health import HealthResponse

router = APIRouter(prefix="/health")


@router.get("", response_model=HealthResponse, summary="Health check")
async def health_check(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
        version=settings.app_version,
    )
