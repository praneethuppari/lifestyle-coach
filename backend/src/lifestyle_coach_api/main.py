from typing_extensions import Annotated

from fastapi import Depends, FastAPI

from lifestyle_coach_api.api.router import api_router
from lifestyle_coach_api.core.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app

app = create_app()
