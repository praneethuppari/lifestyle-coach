from fastapi import FastAPI

from lifestyle_coach_api.api.router import api_router
from lifestyle_coach_api.core.config import get_settings
from lifestyle_coach_api.core.errors import AppError, app_error_handler


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]

    return app


app = create_app()
