import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifestyle_coach_api.core.database import Base

if TYPE_CHECKING:
    from lifestyle_coach_api.models.ingredient import Ingredient
    from lifestyle_coach_api.models.recipe import Recipe


class User(Base):
    """
    Core user identity table.

    Authentication credentials (password hash, OAuth tokens, sessions) are
    intentionally excluded — add them when auth is introduced. This table exists
    now so that user-scoped foreign keys (e.g. user-created ingredients) have a
    valid referent.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient", back_populates="user"
    )
    recipes: Mapped[list["Recipe"]] = relationship(
        "Recipe", back_populates="user"
    )
