from sqlalchemy.orm import Session

from lifestyle_coach_api.models.recipe import Recipe


class RecipeRepository:
    """Data access for the Recipe entity."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, recipe: Recipe) -> Recipe:
        self._db.add(recipe)
        self._db.commit()
        self._db.refresh(recipe)
        return recipe
