import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifestyle_coach_api.core.database import Base

if TYPE_CHECKING:
    from lifestyle_coach_api.models.recipe_ingredient import RecipeIngredient
    from lifestyle_coach_api.models.user import User


class Ingredient(Base):
    """
    A catalog of known ingredients — both globally provided (is_global=True) and
    user-created (is_global=False, user_id set).

    Nutrition values are stored per 100g, which is the industry-standard reference
    amount. This allows callers to derive per-serving macros by scaling:
        nutrient_per_serving = (nutrient_per_100g / 100) * quantity_in_grams

    Barcode (UPC/EAN) enables scanning-based lookup. When a barcode is scanned and
    not found locally, the API should query an external source (e.g. Open Food Facts,
    USDA FoodData Central), persist the result here, and return it — so subsequent
    scans of the same product are served from local storage.
    """

    __tablename__ = "ingredients"
    __table_args__ = (
        # Barcodes must be unique when present.
        # PostgreSQL allows multiple NULL values in a unique constraint (NULL != NULL),
        # so ingredients without a barcode are unconstrained.
        UniqueConstraint("barcode", name="uq_ingredients_barcode"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # e.g. "Kirkland Signature"

    # Barcode (UPC-12 or EAN-13) for scanning-based lookup
    barcode: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Catalog provenance
    # is_global=True  → system-provided common ingredient, shared across all users
    # is_global=False → user-created, scoped to user_id
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )  # null for global ingredients

    # Data source tracking — where the nutrition data came from
    source: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # "usda", "openfoodfacts", "manual", "barcode"
    source_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # external identifier from the source (e.g. USDA FDC ID)

    # Default serving reference — informational, not used for macro calculation
    serving_size_amount: Mapped[float | None] = mapped_column(
        Numeric(7, 2), nullable=True
    )  # e.g. 240
    serving_size_unit: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # e.g. "ml", "g", "cup"

    # Nutrition per 100g (standard reference amount)
    calories_per_100g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    protein_per_100g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    carbs_per_100g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    fat_per_100g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    fiber_per_100g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="ingredients")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(  # noqa: F821
        "RecipeIngredient", back_populates="ingredient"
    )
