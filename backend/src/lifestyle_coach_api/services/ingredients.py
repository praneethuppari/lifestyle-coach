import uuid

from lifestyle_coach_api.core.errors import NotFoundError
from lifestyle_coach_api.models.ingredient import Ingredient
from lifestyle_coach_api.repositories.ingredients import IngredientRepository
from lifestyle_coach_api.schemas.ingredients import IngredientImport, IngredientUpdate


class IngredientService:
    """Business logic for personal ingredient library and catalog access."""

    def __init__(self, repo: IngredientRepository) -> None:
        self._repo = repo

    def import_custom(self, user_id: uuid.UUID, data: IngredientImport) -> Ingredient:
        """Add an ingredient to the user's personal library."""
        ingredient = Ingredient(
            user_id=user_id,
            is_global=False,
            **data.model_dump(exclude_none=True),
        )
        return self._repo.create(ingredient)

    def get_personal(self, user_id: uuid.UUID, ingredient_id: uuid.UUID) -> Ingredient:
        """Return the ingredient only if it exists and belongs to user_id."""
        ingredient = self._repo.get_by_id(ingredient_id)
        if ingredient is None or ingredient.user_id != user_id:
            raise NotFoundError(
                detail=f"Ingredient {ingredient_id} not found.",
                code="ingredient_not_found",
            )
        return ingredient

    def list_personal(
        self,
        user_id: uuid.UUID,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Ingredient], int]:
        return self._repo.list_personal(user_id, q, page, page_size)

    def get_catalog(self, ingredient_id: uuid.UUID) -> Ingredient:
        """Return the ingredient only if it exists and is a global catalog ingredient."""
        ingredient = self._repo.get_by_id(ingredient_id)
        if ingredient is None or not ingredient.is_global:
            raise NotFoundError(
                detail=f"Catalog ingredient {ingredient_id} not found.",
                code="ingredient_not_found",
            )
        return ingredient

    def list_catalog(
        self,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Ingredient], int]:
        return self._repo.list_global(q, page, page_size)

    def update(
        self, user_id: uuid.UUID, ingredient_id: uuid.UUID, data: IngredientUpdate
    ) -> Ingredient:
        """Partially update a personal ingredient. Only set fields are changed."""
        ingredient = self._repo.get_by_id(ingredient_id)
        if ingredient is None or ingredient.user_id != user_id:
            raise NotFoundError(
                detail=f"Ingredient {ingredient_id} not found.",
                code="ingredient_not_found",
            )
        return self._repo.update(ingredient, data.model_dump(exclude_unset=True))

    def delete(self, user_id: uuid.UUID, ingredient_id: uuid.UUID) -> None:
        """Delete a personal ingredient. Raises NotFoundError if missing or not owned."""
        ingredient = self._repo.get_by_id(ingredient_id)
        if ingredient is None or ingredient.user_id != user_id:
            raise NotFoundError(
                detail=f"Ingredient {ingredient_id} not found.",
                code="ingredient_not_found",
            )
        self._repo.delete(ingredient)
