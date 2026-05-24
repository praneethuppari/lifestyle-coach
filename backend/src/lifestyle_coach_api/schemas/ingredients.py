import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class IngredientWriteBase(BaseModel):
    """Shared fields for write models (import and update).

    Includes input validation constraints — not safe to use as a response base
    because Pydantic v2 runs validators against ORM data on model_validate().
    """

    brand: str | None = Field(default=None, max_length=255)
    barcode: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=50)
    source_id: str | None = Field(default=None, max_length=255)
    serving_size_amount: float | None = Field(default=None, ge=0)
    serving_size_unit: str | None = Field(default=None, max_length=20)
    calories_per_100g: float | None = Field(default=None, ge=0)
    protein_per_100g: float | None = Field(default=None, ge=0)
    carbs_per_100g: float | None = Field(default=None, ge=0)
    fat_per_100g: float | None = Field(default=None, ge=0)
    fiber_per_100g: float | None = Field(default=None, ge=0)


class IngredientReadBase(BaseModel):
    """Shared fields for read models (responses).

    No input constraints — safe for ORM validation via model_validate().
    """

    brand: str | None = None
    barcode: str | None = None
    source: str | None = None
    source_id: str | None = None
    serving_size_amount: float | None = None
    serving_size_unit: str | None = None
    calories_per_100g: float | None = None
    protein_per_100g: float | None = None
    carbs_per_100g: float | None = None
    fat_per_100g: float | None = None
    fiber_per_100g: float | None = None


class IngredientImport(IngredientWriteBase):
    """Fields accepted when a user manually adds an ingredient to their library.

    System-managed fields (id, user_id, is_global, created_at, updated_at)
    are excluded — the service layer sets them.
    """

    name: str = Field(max_length=255)


class IngredientUpdate(IngredientWriteBase):
    """Partial update for a personal ingredient. All fields optional."""

    name: str | None = Field(default=None, max_length=255)


class IngredientResponse(IngredientReadBase):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID | None
    is_global: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IngredientListResponse(BaseModel):
    items: list[IngredientResponse]
    total: int
    page: int
    page_size: int
