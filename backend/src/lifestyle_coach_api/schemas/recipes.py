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


class RecipeIngredientItem(BaseModel):
    """Write model for a single ingredient entry within a recipe payload."""

    ingredient_id: uuid.UUID
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)
    preparation: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=255)
    order: int = Field(default=0, ge=0)


class IngredientSummaryResponse(BaseModel):
    """Minimal ingredient details embedded inside a recipe ingredient response."""

    id: uuid.UUID
    name: str
    brand: str | None = None

    model_config = {"from_attributes": True}


class RecipeIngredientResponse(BaseModel):
    """A single ingredient line in a recipe response.

    Nests an IngredientSummaryResponse alongside the recipe-specific association
    fields (quantity, unit, preparation, notes, order). Pydantic resolves the
    nested `ingredient` attribute automatically via from_attributes.
    """

    ingredient_id: uuid.UUID
    ingredient: IngredientSummaryResponse
    quantity: float | None = None
    unit: str | None = None
    preparation: str | None = None
    notes: str | None = None
    order: int

    model_config = {"from_attributes": True}


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
    ingredients: list[RecipeIngredientItem] = Field(default_factory=list)


class RecipeUpdate(RecipeWriteBase):
    """Partial update for a recipe. All fields optional.

    If ingredients is provided, it fully replaces the recipe's current ingredient set.
    If ingredients is absent, the existing ingredient rows are left untouched.
    """

    title: str | None = Field(default=None, max_length=255)
    serving_unit: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None
    ingredients: list[RecipeIngredientItem] | None = None


class RecipeResponse(RecipeReadBase):
    id: uuid.UUID
    user_id: uuid.UUID | None
    title: str
    source_type: RecipeSourceType | None
    is_global: bool
    is_verified: bool
    serving_unit: str
    tags: list[str]
    ingredients: list[RecipeIngredientResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    items: list[RecipeResponse]
    total: int
    page: int
    page_size: int
