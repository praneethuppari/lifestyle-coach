import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from lifestyle_coach_api.api.dependencies import get_current_user_id
from lifestyle_coach_api.core.database import get_db
from lifestyle_coach_api.repositories.recipes import RecipeRepository
from lifestyle_coach_api.schemas.recipes import (
    RecipeImport,
    RecipeListResponse,
    RecipeResponse,
    RecipeUpdate,
)
from lifestyle_coach_api.services.recipes import RecipeService

# ---------------------------------------------------------------------------
# Shared dependency
# ---------------------------------------------------------------------------


def get_recipe_service(db: Annotated[Session, Depends(get_db)]) -> RecipeService:
    return RecipeService(RecipeRepository(db))


# ---------------------------------------------------------------------------
# Personal recipes router  —  /recipes
# ---------------------------------------------------------------------------

personal_router = APIRouter(prefix="/recipes", tags=["recipes"])


@personal_router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import a custom recipe",
)
def import_recipe(
    body: RecipeImport,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    recipe = service.import_custom(user_id, body)
    return RecipeResponse.model_validate(recipe)


@personal_router.get(
    "",
    response_model=RecipeListResponse,
    summary="List or search the caller's personal recipes",
)
def list_personal_recipes(
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> RecipeListResponse:
    items, total = service.list_personal(user_id, q, page, page_size)
    return RecipeListResponse(
        items=[RecipeResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@personal_router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get a personal recipe by ID",
)
def get_personal_recipe(
    recipe_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    recipe = service.get_personal(user_id, recipe_id)
    return RecipeResponse.model_validate(recipe)


@personal_router.patch(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Partially update a personal recipe's metadata",
)
def update_personal_recipe(
    recipe_id: uuid.UUID,
    body: RecipeUpdate,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    recipe = service.update(user_id, recipe_id, body)
    return RecipeResponse.model_validate(recipe)


@personal_router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a personal recipe",
)
def delete_personal_recipe(
    recipe_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> None:
    service.delete(user_id, recipe_id)


# ---------------------------------------------------------------------------
# Catalog router  —  /catalog/recipes  (read-only, global recipes)
# ---------------------------------------------------------------------------

catalog_router = APIRouter(
    prefix="/catalog/recipes",
    tags=["catalog"],
    dependencies=[Depends(get_current_user_id)],
)


@catalog_router.get(
    "",
    response_model=RecipeListResponse,
    summary="List or search the global recipe catalog",
)
def list_catalog_recipes(
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> RecipeListResponse:
    items, total = service.list_catalog(q, page, page_size)
    return RecipeListResponse(
        items=[RecipeResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@catalog_router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get a global catalog recipe by ID",
)
def get_catalog_recipe(
    recipe_id: uuid.UUID,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    recipe = service.get_catalog(recipe_id)
    return RecipeResponse.model_validate(recipe)
