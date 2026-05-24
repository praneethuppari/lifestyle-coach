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


class RecipeWriteBase(BaseModel):
    """Shared fields for write models (import and update).

    Includes input validation constraints — not safe to use as a response base
    because Pydantic v2 runs validators against ORM data on model_validate().
    """

    description: str | None = None
    image_url: str | None = Field(default=None, max_length=2048)
    source_url: str | None = Field(default=None, max_length=2048)
    source_author: str | None = Field(default=None, max_length=255)
    cuisine: str | None = Field(default=None, max_length=100)
    difficulty: RecipeDifficulty | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    serving_weight_g: float | None = Field(default=None, ge=0)
    instructions: list[RecipeInstructionStep] | None = None
    calories: float | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0)
    carbs_g: float | None = Field(default=None, ge=0)
    fat_g: float | None = Field(default=None, ge=0)
    fiber_g: float | None = Field(default=None, ge=0)


class RecipeReadBase(BaseModel):
    """Shared fields for read models (responses).

    No input constraints — safe for ORM validation via model_validate().
    """

    description: str | None = None
    image_url: str | None = None
    source_url: str | None = None
    source_author: str | None = None
    cuisine: str | None = None
    difficulty: RecipeDifficulty | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int | None = None
    serving_weight_g: float | None = None
    instructions: list[RecipeInstructionStep] | None = None
    calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None


class RecipeImport(RecipeWriteBase):
    """Fields accepted when a user manually imports a custom recipe.

    System-managed fields (id, user_id, source_type, is_global, is_verified,
    created_at, updated_at) are excluded — the service layer sets them.
    """

    title: str = Field(max_length=255)
    serving_unit: str = "portion"
    tags: list[str] = Field(default_factory=list)


class RecipeUpdate(RecipeWriteBase):
    """Partial metadata update for a recipe. All fields optional. No ingredients."""

    title: str | None = Field(default=None, max_length=255)
    serving_unit: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None


class RecipeResponse(RecipeReadBase):
    id: uuid.UUID
    user_id: uuid.UUID | None
    title: str
    source_type: RecipeSourceType | None
    is_global: bool
    is_verified: bool
    serving_unit: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    items: list[RecipeResponse]
    total: int
    page: int
    page_size: int
