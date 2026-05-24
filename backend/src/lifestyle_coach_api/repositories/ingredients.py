import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from lifestyle_coach_api.models.ingredient import Ingredient


class IngredientRepository:
    """Data access for the Ingredient entity."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, ingredient: Ingredient) -> Ingredient:
        self._db.add(ingredient)
        self._db.commit()
        self._db.refresh(ingredient)
        return ingredient

    def get_by_id(self, ingredient_id: uuid.UUID) -> Ingredient | None:
        return self._db.get(Ingredient, ingredient_id)

    def list_personal(
        self,
        user_id: uuid.UUID,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Ingredient], int]:
        """Return (ingredients, total) for the given user, optionally filtered by name."""
        base = select(Ingredient).where(
            Ingredient.user_id == user_id,
            Ingredient.is_global.is_(False),
        )
        if q:
            base = base.where(Ingredient.name.ilike(f"%{q}%"))
        total: int = (
            self._db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        )
        ingredients = list(
            self._db.scalars(
                base.order_by(Ingredient.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return ingredients, total

    def list_global(
        self,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Ingredient], int]:
        """Return (ingredients, total) for global catalog ingredients, optionally filtered by name."""
        base = select(Ingredient).where(Ingredient.is_global.is_(True))
        if q:
            base = base.where(Ingredient.name.ilike(f"%{q}%"))
        total: int = (
            self._db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        )
        ingredients = list(
            self._db.scalars(
                base.order_by(Ingredient.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return ingredients, total

    def update(self, ingredient: Ingredient, data: dict) -> Ingredient:
        for key, value in data.items():
            setattr(ingredient, key, value)
        self._db.commit()
        self._db.refresh(ingredient)
        return ingredient

    def delete(self, ingredient: Ingredient) -> None:
        self._db.delete(ingredient)
        self._db.commit()
