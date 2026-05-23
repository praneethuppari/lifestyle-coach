import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from lifestyle_coach_api.core.database import get_db
from lifestyle_coach_api.repositories.recipes import RecipeRepository
from lifestyle_coach_api.schemas.recipes import RecipeImport, RecipeResponse
from lifestyle_coach_api.services.recipes import RecipeService

router = APIRouter(prefix="/users/{user_id}/recipes", tags=["recipes"])


def get_recipe_service(db: Annotated[Session, Depends(get_db)]) -> RecipeService:
    return RecipeService(RecipeRepository(db))


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import a custom recipe for a user",
)
def import_recipe(
    user_id: uuid.UUID,
    body: RecipeImport,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    recipe = service.import_custom(user_id, body)
    return RecipeResponse.model_validate(recipe)
