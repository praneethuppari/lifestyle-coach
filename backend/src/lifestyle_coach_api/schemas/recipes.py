import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from lifestyle_coach_api.models.recipe import RecipeDifficulty, RecipeSourceType


class RecipeInstructionStep(BaseModel):
    """A single numbered step in a recipe's cooking instructions."""

    step: int
    instruction: str
    duration_minutes: int | None = None
    tip: str | None = None


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
    serving_unit: str = "portion"
    serving_weight_g: float | None = Field(default=None, ge=0)
    instructions: list[RecipeInstructionStep] | None = None
    calories: float | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    tags: list[str] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    """Partial metadata update for a recipe. All fields optional. No ingredients."""

    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=2048)
    source_url: str | None = Field(default=None, max_length=2048)
    source_author: str | None = Field(default=None, max_length=255)
    cuisine: str | None = Field(default=None, max_length=100)
    difficulty: RecipeDifficulty | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    serving_unit: str | None = Field(default=None, max_length=50)
    serving_weight_g: float | None = Field(default=None, ge=0)
    instructions: list[RecipeInstructionStep] | None = None
    calories: float | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    tags: list[str] | None = None


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
    serving_unit: str
    serving_weight_g: float | None
    instructions: list[RecipeInstructionStep] | None
    calories: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    fiber_g: float | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    items: list[RecipeResponse]
    total: int
    page: int
    page_size: int
