import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from lifestyle_coach_api.models.recipe import RecipeDifficulty, RecipeSourceType


class RecipeImport(BaseModel):
    """Fields accepted when a user manually imports a custom recipe.

    System-managed fields (id, user_id, source_type, is_global, is_verified,
    created_at, updated_at) are excluded — the service layer sets them.
    """

    title: str = Field(max_length=255)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=2048)
    source_url: str | None = Field(default=None, max_length=2048)
    source_author: str | None = Field(default=None, max_length=255)
    cuisine: str | None = Field(default=None, max_length=100)
    difficulty: RecipeDifficulty | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    # Each step: {"step": int, "instruction": str, "duration_minutes": int|None, "tip": str|None}
    instructions: list[dict[str, Any]] | None = None
    calories: float | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    tags: list[str] = Field(default_factory=list)


class RecipeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    title: str
    description: str | None
    image_url: str | None
    source_url: str | None
    source_type: RecipeSourceType | None
    source_author: str | None
    is_global: bool
    is_verified: bool
    cuisine: str | None
    difficulty: RecipeDifficulty | None
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    servings: int | None
    instructions: list[dict[str, Any]] | None
    calories: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    fiber_g: float | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
