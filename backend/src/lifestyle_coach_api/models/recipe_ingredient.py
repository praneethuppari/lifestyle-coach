import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifestyle_coach_api.core.database import Base

if TYPE_CHECKING:
    from lifestyle_coach_api.models.ingredient import Ingredient
    from lifestyle_coach_api.models.recipe import Recipe


class RecipeIngredient(Base):
    """
    Join table linking a Recipe to an Ingredient with the quantity and context
    specific to that recipe.

    Quantities are stored as entered by the recipe author (e.g. "2 cups", "200 g").
    For macro calculation, callers should convert quantity to grams and scale the
    Ingredient's per-100g nutrition values accordingly.

    The `order` field controls display sequence in the ingredient list and can also
    be used to group ingredients by section (e.g. "for the marinade" vs "for the
    sauce") when combined with a future `section` field.
    """

    __tablename__ = "recipe_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Quantity as entered — unit determines how to interpret the amount
    quantity: Mapped[float | None] = mapped_column(
        Numeric(10, 3), nullable=True
    )  # e.g. 240, 2, 0.5
    unit: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )  # e.g. "g", "ml", "cup", "tbsp", "whole"

    # Contextual notes for this use of the ingredient in this recipe
    preparation: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # e.g. "finely chopped", "room temperature"
    notes: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # e.g. "divided", "plus more for garnish"

    # Display order within the recipe's ingredient list (0-indexed)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    recipe: Mapped["Recipe"] = relationship(  # noqa: F821
        "Recipe", back_populates="ingredients"
    )
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient", back_populates="recipe_ingredients"
    )
