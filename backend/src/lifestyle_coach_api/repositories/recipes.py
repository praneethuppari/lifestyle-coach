import uuid

from sqlalchemy import func, select
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

    def get_by_id(self, recipe_id: uuid.UUID) -> Recipe | None:
        return self._db.get(Recipe, recipe_id)

    def list_personal(
        self,
        user_id: uuid.UUID,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Recipe], int]:
        """Return (recipes, total) for the given user, optionally filtered by title."""
        base = select(Recipe).where(
            Recipe.user_id == user_id,
            Recipe.is_global.is_(False),
        )
        if q:
            base = base.where(Recipe.title.ilike(f"%{q}%"))
        total: int = (
            self._db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        )
        recipes = list(
            self._db.scalars(
                base.order_by(Recipe.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return recipes, total

    def list_global(
        self,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Recipe], int]:
        """Return (recipes, total) for global catalog recipes, optionally filtered by title."""
        base = select(Recipe).where(Recipe.is_global.is_(True))
        if q:
            base = base.where(Recipe.title.ilike(f"%{q}%"))
        total: int = (
            self._db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        )
        recipes = list(
            self._db.scalars(
                base.order_by(Recipe.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return recipes, total

    def update(self, recipe: Recipe, data: dict) -> Recipe:
        for key, value in data.items():
            setattr(recipe, key, value)
        self._db.commit()
        self._db.refresh(recipe)
        return recipe

    def delete(self, recipe: Recipe) -> None:
        self._db.delete(recipe)
        self._db.commit()
