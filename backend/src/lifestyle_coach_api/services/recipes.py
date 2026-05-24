import uuid

from lifestyle_coach_api.core.errors import NotFoundError
from lifestyle_coach_api.models.recipe import Recipe, RecipeSourceType
from lifestyle_coach_api.repositories.recipes import RecipeRepository
from lifestyle_coach_api.schemas.recipes import RecipeImport, RecipeUpdate


class RecipeService:
    """Business logic for recipe import and management."""

    def __init__(self, repo: RecipeRepository) -> None:
        self._repo = repo

    def import_custom(self, user_id: uuid.UUID, data: RecipeImport) -> Recipe:
        """Create a user-owned, manually entered recipe with source_type=manual."""
        recipe = Recipe(
            user_id=user_id,
            source_type=RecipeSourceType.manual,
            is_global=False,
            **data.model_dump(exclude_none=True),
        )
        return self._repo.create(recipe)

    def get_personal(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> Recipe:
        """Return the recipe only if it exists and belongs to user_id."""
        recipe = self._repo.get_by_id(recipe_id)
        if recipe is None or recipe.user_id != user_id:
            raise NotFoundError(
                detail=f"Recipe {recipe_id} not found.",
                code="recipe_not_found",
            )
        return recipe

    def list_personal(
        self,
        user_id: uuid.UUID,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Recipe], int]:
        return self._repo.list_personal(user_id, q, page, page_size)

    def get_catalog(self, recipe_id: uuid.UUID) -> Recipe:
        """Return the recipe only if it exists and is a global catalog recipe."""
        recipe = self._repo.get_by_id(recipe_id)
        if recipe is None or not recipe.is_global:
            raise NotFoundError(
                detail=f"Catalog recipe {recipe_id} not found.",
                code="recipe_not_found",
            )
        return recipe

    def list_catalog(
        self,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Recipe], int]:
        return self._repo.list_global(q, page, page_size)

    def update(
        self, user_id: uuid.UUID, recipe_id: uuid.UUID, data: RecipeUpdate
    ) -> Recipe:
        """Partially update a user-owned recipe. Only set fields are changed."""
        recipe = self._repo.get_by_id(recipe_id)
        if recipe is None or recipe.user_id != user_id:
            raise NotFoundError(
                detail=f"Recipe {recipe_id} not found.",
                code="recipe_not_found",
            )
        return self._repo.update(recipe, data.model_dump(exclude_unset=True))

    def delete(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> None:
        """Delete a user-owned recipe. Raises NotFoundError if missing or not owned."""
        recipe = self._repo.get_by_id(recipe_id)
        if recipe is None or recipe.user_id != user_id:
            raise NotFoundError(
                detail=f"Recipe {recipe_id} not found.",
                code="recipe_not_found",
            )
        self._repo.delete(recipe)
