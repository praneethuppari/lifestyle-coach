import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifestyle_coach_api.core.database import Base

if TYPE_CHECKING:
    from lifestyle_coach_api.models.recipe_ingredient import RecipeIngredient
    from lifestyle_coach_api.models.user import User


class RecipeDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class RecipeSourceType(str, enum.Enum):
    manual = "manual"
    instagram = "instagram"
    url = "url"


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Source info — where the recipe came from
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    source_type: Mapped[RecipeSourceType | None] = mapped_column(
        Enum(RecipeSourceType, name="recipe_source_type"),
        nullable=True,
    )
    source_author: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # creator attribution for imported recipes
    is_verified: Mapped[bool] = mapped_column(default=False)

    # Ownership — null user_id means this is a global/system recipe
    is_global: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Display
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Classification — used for taste profile matching and recommendation filtering
    cuisine: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # e.g. "italian", "mexican", "japanese"
    difficulty: Mapped[RecipeDifficulty | None] = mapped_column(
        Enum(RecipeDifficulty, name="recipe_difficulty"),
        nullable=True,
    )

    # Cooking info
    prep_time_minutes: Mapped[int | None] = mapped_column(nullable=True)
    cook_time_minutes: Mapped[int | None] = mapped_column(nullable=True)
    servings: Mapped[int | None] = mapped_column(nullable=True, server_default="1")
    serving_unit: Mapped[str] = mapped_column(
        String(50), nullable=False, default="portion", server_default="portion"
    )
    serving_weight_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)

    # Instructions — step-by-step cooking execution guidance.
    # Schema per object: {"step": int, "instruction": str,
    #                     "duration_minutes": int | None, "tip": str | None}
    instructions: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Macros per serving (stored as decimals for precision)
    calories: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    carbs_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    fiber_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)

    # Tags for filtering and recommendations (e.g. ["italian", "high-protein", "quick"])
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="recipes")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(  # noqa: F821
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
