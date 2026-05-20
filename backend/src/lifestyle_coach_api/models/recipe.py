import uuid
from datetime import datetime, timezone

from sqlalchemy import ARRAY, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from lifestyle_coach_api.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Source info — where the recipe came from
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    source_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g. "manual", "instagram", "url"
    is_verified: Mapped[bool] = mapped_column(default=False)

    # Cooking info
    prep_time_minutes: Mapped[int | None] = mapped_column(nullable=True)
    cook_time_minutes: Mapped[int | None] = mapped_column(nullable=True)
    servings: Mapped[int | None] = mapped_column(nullable=True)

    # Macros per serving (stored as decimals for precision)
    calories: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    carbs_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)

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
