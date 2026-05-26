import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from lifestyle_coach_api.api.dependencies import get_current_user_id
from lifestyle_coach_api.core.database import get_db
from lifestyle_coach_api.repositories.ingredients import IngredientRepository
from lifestyle_coach_api.schemas.ingredients import (
    IngredientImport,
    IngredientListResponse,
    IngredientResponse,
    IngredientUpdate,
)
from lifestyle_coach_api.services.ingredients import IngredientService

# ---------------------------------------------------------------------------
# Shared dependency
# ---------------------------------------------------------------------------


def get_ingredient_service(db: Annotated[Session, Depends(get_db)]) -> IngredientService:
    return IngredientService(IngredientRepository(db))


# ---------------------------------------------------------------------------
# Personal ingredients router  —  /ingredients
# ---------------------------------------------------------------------------

personal_router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@personal_router.post(
    "",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an ingredient to the caller's personal library",
)
def import_ingredient(
    body: IngredientImport,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientResponse:
    ingredient = service.import_custom(user_id, body)
    return IngredientResponse.model_validate(ingredient)


@personal_router.get(
    "",
    response_model=IngredientListResponse,
    summary="List or search the caller's personal ingredient library",
)
def list_personal_ingredients(
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> IngredientListResponse:
    items, total = service.list_personal(user_id, q, page, page_size)
    return IngredientListResponse(
        items=[IngredientResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@personal_router.get(
    "/{ingredient_id}",
    response_model=IngredientResponse,
    summary="Get a personal ingredient by ID",
)
def get_personal_ingredient(
    ingredient_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientResponse:
    ingredient = service.get_personal(user_id, ingredient_id)
    return IngredientResponse.model_validate(ingredient)


@personal_router.patch(
    "/{ingredient_id}",
    response_model=IngredientResponse,
    summary="Partially update a personal ingredient",
)
def update_ingredient(
    ingredient_id: uuid.UUID,
    body: IngredientUpdate,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientResponse:
    ingredient = service.update(user_id, ingredient_id, body)
    return IngredientResponse.model_validate(ingredient)


@personal_router.delete(
    "/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a personal ingredient",
)
def delete_ingredient(
    ingredient_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> None:
    service.delete(user_id, ingredient_id)


# ---------------------------------------------------------------------------
# Catalog ingredients router  —  /catalog/ingredients
# ---------------------------------------------------------------------------

catalog_router = APIRouter(
    prefix="/catalog/ingredients",
    tags=["catalog"],
    dependencies=[Depends(get_current_user_id)],
)


@catalog_router.get(
    "",
    response_model=IngredientListResponse,
    summary="List or search the global ingredient catalog",
)
def list_catalog_ingredients(
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> IngredientListResponse:
    items, total = service.list_catalog(q, page, page_size)
    return IngredientListResponse(
        items=[IngredientResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@catalog_router.get(
    "/{ingredient_id}",
    response_model=IngredientResponse,
    summary="Get a global catalog ingredient by ID",
)
def get_catalog_ingredient(
    ingredient_id: uuid.UUID,
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientResponse:
    ingredient = service.get_catalog(ingredient_id)
    return IngredientResponse.model_validate(ingredient)
