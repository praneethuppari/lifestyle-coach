# Ingredient Library

## What This Feature Does

Gives users a personal ingredient library they can build over time. Ingredients are independent resources with per-100g nutrition data. A global read-only catalog provides system-supplied ingredients that any user can reference. Ingredients attach to recipes via an embedded array in the recipe payload — creating or updating a recipe now accepts an optional `ingredients[]` list that is persisted in the same transaction.

## Endpoints

### Personal ingredient library — full CRUD, auth required

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/ingredients` | Add ingredient to personal library |
| `GET` | `/api/v1/ingredients?q=&page=&page_size=` | List / search personal library (paginated) |
| `GET` | `/api/v1/ingredients/{ingredient_id}` | Get a personal ingredient by ID |
| `PATCH` | `/api/v1/ingredients/{ingredient_id}` | Partial update |
| `DELETE` | `/api/v1/ingredients/{ingredient_id}` | Delete |

**Request body for POST** (`IngredientImport`):
```json
{
  "name": "Chicken breast",
  "brand": "Tyson",
  "barcode": "0123456789012",
  "calories_per_100g": 165,
  "protein_per_100g": 31,
  "carbs_per_100g": 0,
  "fat_per_100g": 3.6,
  "fiber_per_100g": 0,
  "serving_size_amount": 100,
  "serving_size_unit": "g"
}
```
All fields except `name` are optional.

**Response** (`IngredientResponse`):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "Chicken breast",
  "brand": null,
  "barcode": null,
  "is_global": false,
  "source": null,
  "source_id": null,
  "serving_size_amount": null,
  "serving_size_unit": null,
  "calories_per_100g": 165.0,
  "protein_per_100g": 31.0,
  "carbs_per_100g": 0.0,
  "fat_per_100g": 3.6,
  "fiber_per_100g": null,
  "created_at": "...",
  "updated_at": "..."
}
```

**Error cases:** `404` for get/patch/delete when ingredient does not exist or belongs to a different user (ownership leakage prevention). `422` for missing `name`, invalid UUID path params, or missing `X-User-Id` header.

---

### Global ingredient catalog — read-only

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/catalog/ingredients?q=&page=&page_size=` | List / search global catalog (paginated) |
| `GET` | `/api/v1/catalog/ingredients/{ingredient_id}` | Get a catalog ingredient by ID |

No `X-User-Id` required. Returns `404` if the ingredient does not exist or is not global.

---

### Recipe endpoints — extended to support ingredients

| Method | Path | Change |
|--------|------|--------|
| `POST` | `/api/v1/users/{user_id}/recipes` | Accepts optional `ingredients[]` |
| `PATCH` | `/api/v1/recipes/{recipe_id}` | Accepts optional `ingredients[]` (full replacement) |
| `GET` | `/api/v1/recipes/{recipe_id}` | Response now embeds `ingredients[]` |
| `GET` | `/api/v1/catalog/recipes/{recipe_id}` | Response now embeds `ingredients[]` |
| `GET` | `/api/v1/recipes` | Response items now embed `ingredients[]` |
| `GET` | `/api/v1/catalog/recipes` | Response items now embed `ingredients[]` |

**Ingredient item in request** (`RecipeIngredientItem`):
```json
{
  "ingredient_id": "uuid",
  "quantity": 200,
  "unit": "g",
  "preparation": "finely chopped",
  "notes": "divided",
  "order": 0
}
```
Only `ingredient_id` is required.

**Ingredient item in response** (`RecipeIngredientResponse`, embedded in `RecipeResponse.ingredients`):
```json
{
  "ingredient_id": "uuid",
  "name": "Chicken breast",
  "brand": null,
  "quantity": 200.0,
  "unit": "g",
  "preparation": null,
  "notes": null,
  "order": 0
}
```

## Schema and Model Changes

### New schemas — `schemas/ingredients.py`
- `IngredientWriteBase` — shared write fields with input constraints
- `IngredientReadBase` — shared read fields, no constraints (safe for ORM validation)
- `IngredientImport(IngredientWriteBase)` — requires `name`
- `IngredientUpdate(IngredientWriteBase)` — all fields optional
- `IngredientResponse(IngredientReadBase)` — `from_attributes = True`
- `IngredientListResponse` — paginated wrapper

### Extended schemas — `schemas/recipes.py`
- `RecipeIngredientItem` — write type for embedding ingredients in recipe payloads
- `RecipeIngredientResponse` — read type; flattens `RecipeIngredient` join row + nested `Ingredient` into a flat shape via `model_validator(mode="before")`
- `RecipeImport` — added `ingredients: list[RecipeIngredientItem]` (default empty)
- `RecipeUpdate` — added `ingredients: list[RecipeIngredientItem] | None` (absent = no-op)
- `RecipeResponse` — added `ingredients: list[RecipeIngredientResponse]` with `validation_alias=AliasChoices("ingredients", "recipe_ingredients")` to bridge the ORM attribute name (`recipe_ingredients`) to the response key (`ingredients`)

No DB migration needed — `ingredients` and `recipe_ingredients` tables were in the initial schema.

## Architecture Notes

Layer responsibilities follow the same pattern as `feature/manual-recipe-import`:

| Layer | Responsibility |
|-------|---------------|
| Route | Validate request shape, call service, call `model_validate()` on result |
| Service | Enforce ownership, orchestrate ingredient attachment on recipe create/update |
| Repository | Data access only; handles eager-loading of `recipe_ingredients.ingredient` |
| Schema | Input validation (write bases) and ORM serialization (read bases) |

**Eager loading:** `RecipeRepository.get_by_id` uses `selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)` so ingredient names are available without a second query when building the response.

**Ingredient attachment on create:** The service builds `RecipeIngredient` objects and assigns them to `recipe.recipe_ingredients` before calling `repo.create()`. SQLAlchemy's `cascade="all, delete-orphan"` on the relationship persists them in the same `commit`.

**Full-replacement semantics on update:** If `ingredients` is present in a PATCH payload, the repository deletes the current set and inserts the new set in one transaction (by reassigning `recipe.recipe_ingredients`). If absent, the ingredient rows are untouched.

## Design Decisions

**Ingredients embedded in recipe payload, not via nested routes.** A recipe is one document — a recipe form submits all fields at once. Separate `POST /recipes/{id}/ingredients` endpoints add API surface with no corresponding user action. Payload size is negligible (20 ingredients × 5 small fields ≈ 2–3 KB). See `BRANCHES.md` decisions log for full rationale.

**Flat `RecipeIngredientResponse` shape.** Rather than nesting `{ ingredient_id, ingredient: { name, brand }, quantity, ... }`, the response flattens `name` and `brand` alongside the association fields. This is handled by `model_validator(mode="before")` in `RecipeIngredientResponse` which transforms the ORM join object before Pydantic field validation runs. Frontend consumers get a clean flat array.

**`AliasChoices` on `RecipeResponse.ingredients`.** The ORM attribute is named `recipe_ingredients` (to avoid shadowing the concept of "ingredients" at the recipe level), but the API response key should be `ingredients`. `validation_alias=AliasChoices("ingredients", "recipe_ingredients")` lets Pydantic accept both names on input while always outputting `ingredients`.

**`SimpleNamespace` in tests.** Creating real `Recipe` SQLAlchemy ORM objects in tests and assigning non-ORM items to relationship collections triggers SQLAlchemy's backref machinery, which raises `AttributeError: '_sa_instance_state'`. All recipe test factories now return `SimpleNamespace`, which satisfies Pydantic's `from_attributes=True` (plain `getattr` access) without any ORM overhead.

**No migration.** The `ingredients` and `recipe_ingredients` tables were created in the initial schema (`abfaa71b1225`). This branch adds only the API layer on top of existing tables.

## Test Coverage

**`tests/test_ingredients.py`** — 22 tests across 6 classes:
- `TestImportIngredient` (5) — happy path, missing name, missing auth header, correct user ID passed, nutrition fields
- `TestListPersonalIngredients` (4) — paginated list, empty, query/pagination forwarded, missing auth header
- `TestGetPersonalIngredient` (3) — found, 404, invalid UUID
- `TestUpdateIngredient` (3) — updated, 404, only set fields forwarded
- `TestDeleteIngredient` (2) — 204, 404
- `TestListCatalogIngredients` (4) — paginated list, empty, query/pagination forwarded, no auth required
- `TestGetCatalogIngredient` (3) — found, 404, invalid UUID

**`tests/test_recipes.py`** — 5 new tests in `TestRecipeWithIngredients`:
- Import recipe with ingredients → response embeds ingredient list
- Import recipe passes ingredient items to service
- Import recipe with no ingredients → empty `ingredients` array in response
- PATCH with `ingredients` → full replacement passed to service
- PATCH without `ingredients` key → `ingredients` field is unset (service does not replace)

## What Is Explicitly Deferred

- **Barcode-based ingredient lookup** (scan → query Open Food Facts / USDA → persist) — deferred to a future `feature/barcode-scan` branch
- **Ingredient attachment to catalog recipes** — catalog recipes are read-only; the staff tooling to seed the catalog is out of scope for the MVP API
- **Macro derivation from ingredients** — computing recipe-level macros from ingredient quantities and per-100g values is deferred to a future `feature/macro-calculation` branch
- **Individual nested ingredient endpoints** (`POST /recipes/{id}/ingredients`, `DELETE /recipes/{id}/ingredients/{id}`) — intentionally omitted; full-replacement via PATCH covers all real user actions
