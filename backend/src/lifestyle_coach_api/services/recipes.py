import uuid

from lifestyle_coach_api.models.recipe import Recipe, RecipeSourceType
from lifestyle_coach_api.repositories.recipes import RecipeRepository
from lifestyle_coach_api.schemas.recipes import RecipeImport


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
