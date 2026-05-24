# Manual Recipe Import

## What This Feature Does

Allows a user to manually create, browse, update, and delete recipes under their account. Covers the full recipe metadata lifecycle — title, description, macros, structured instructions, serving info, cuisine, timing, and tags. No ingredients are attached at this stage (that is `feature/ingredient-library`). The feature also exposes a read-only global catalog so clients can browse system-curated recipes.

## Endpoints

### Register a User
```
POST /api/v1/users
```

**Request body:**
```json
{
  "email": "alice@example.com",
  "display_name": "Alice"          // optional
}
```

**Success:** `201 Created` with the created user object.  
**Errors:**
- `409 USER_ALREADY_EXISTS` — email is already registered.
- `422` — email is missing or not a valid email address.

---

### Import a Custom Recipe (legacy endpoint — will be cleaned up in feature/basic-auth)
```
POST /api/v1/users/{user_id}/recipes
```

**Request body:** same shape as below (see Personal Recipes section).  
**Success:** `201 Created`.

---

### Personal Recipes

All endpoints below use a temporary `X-User-Id: <uuid>` request header to identify the caller. This header is extracted by the `get_current_user_id` dependency in `api/dependencies.py`. In `feature/basic-auth`, that dependency will be replaced with JWT token extraction and callers will not need to change.

**Missing or non-UUID `X-User-Id` header → `422 Unprocessable Entity`.**

#### List / search personal recipes
```
GET /api/v1/recipes?q=<string>&page=<int>&page_size=<int>
```
- `q` — optional case-insensitive title filter (`ILIKE`).
- `page` — 1-based, default `1`.
- `page_size` — default `20`.

**Success:** `200 OK`
```json
{
  "items": [ ...RecipeResponse ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

#### Get a personal recipe
```
GET /api/v1/recipes/{recipe_id}
```
**Success:** `200 OK` with `RecipeResponse`.  
**Errors:** `404` — not found or not owned by the caller (same response for both to avoid leaking existence).

#### Partially update a personal recipe
```
PATCH /api/v1/recipes/{recipe_id}
```
All body fields are optional. Only fields present in the request body are updated (`exclude_unset` semantics).

**Request body (all optional):**
```json
{
  "title": "Updated Name",
  "description": "...",
  "cuisine": "japanese",
  "difficulty": "medium",
  "prep_time_minutes": 10,
  "cook_time_minutes": 25,
  "servings": 2,
  "serving_unit": "bowl",
  "serving_weight_g": 350.0,
  "instructions": [
    { "step": 1, "instruction": "Boil water", "duration_minutes": 5, "tip": null }
  ],
  "calories": 500.0,
  "protein_g": 30.0,
  "carbs_g": 60.0,
  "fat_g": 15.0,
  "fiber_g": 4.0,
  "tags": ["quick", "healthy"],
  "image_url": "https://...",
  "source_url": "https://...",
  "source_author": "..."
}
```

**Success:** `200 OK` with updated `RecipeResponse`.  
**Errors:** `404` — not found or not owned; `422` — invalid field value.

#### Delete a personal recipe
```
DELETE /api/v1/recipes/{recipe_id}
```
**Success:** `204 No Content`.  
**Errors:** `404` — not found or not owned.

---

### Global Catalog (read-only)

Catalog endpoints do not require the `X-User-Id` header. They are read-only; no mutations are exposed.

#### List / search catalog recipes
```
GET /api/v1/catalog/recipes?q=<string>&page=<int>&page_size=<int>
```
Same query parameters and response shape as personal list above.

#### Get a catalog recipe
```
GET /api/v1/catalog/recipes/{recipe_id}
```
**Success:** `200 OK` with `RecipeResponse` where `is_global=true`.  
**Errors:** `404` — not found or `is_global` is false (both return the same 404 to avoid leaking existence).

---

## Schema and Model Changes

### New Pydantic schemas (`schemas/recipes.py`)
| Schema | Purpose |
|---|---|
| `RecipeInstructionStep` | Typed instruction step: `step` (int, required), `instruction` (str, required), `duration_minutes` (int\|None), `tip` (str\|None) |
| `RecipeUpdate` | All-optional partial update payload for `PATCH /recipes/{id}` |
| `RecipeListResponse` | Paginated list envelope: `items`, `total`, `page`, `page_size` |

### Updated schemas
- `RecipeImport.instructions` changed from `list[dict[str, Any]] | None` → `list[RecipeInstructionStep] | None`.
- `RecipeImport` gains `serving_unit: str = "portion"` and `serving_weight_g: float | None`.
- `RecipeResponse` gains `serving_unit: str` and `serving_weight_g: float | None`.
- `RecipeResponse.instructions` updated to `list[RecipeInstructionStep] | None` — Pydantic v2 coerces the JSONB dicts to typed models via `from_attributes=True`.

### SQLAlchemy model (`models/recipe.py`)
- `servings`: `server_default="1"` added.
- `serving_unit`: new `String(50)`, not null, `default="portion"`, `server_default="portion"`.
- `serving_weight_g`: new `Numeric(7,2)`, nullable.

### Migration
`alembic/versions/3f7a2b8c1e0d_add_serving_fields_to_recipes.py`

---

## Architecture Notes

This feature follows the **Route → Service → Repository** pattern established in `docs/features/backend-framework.md`.

### Caller identity (pre-auth)
The `get_current_user_id` dependency in `api/dependencies.py` reads `X-User-Id: <uuid>` from the request header and returns it as `uuid.UUID`. FastAPI handles header extraction and UUID coercion; a missing or malformed header returns `422` automatically. The `feature/basic-auth` branch will replace this single function with JWT extraction — route signatures do not change.

### Separate namespaces for personal vs. catalog
Personal recipes (`/recipes`) and catalog recipes (`/catalog/recipes`) are on separate endpoint trees, not unified with a `?source=` query parameter. They differ in authorization (catalog is read-only at the API level), ownership semantics (`user_id` vs. system-owned), and CRUD surface. A query param would force authorization branching inside handler logic and mislead consumers about which verbs apply.

### 404 for ownership violations
`get_personal` and `delete`/`update` in `RecipeService` return the same `404 NOT_FOUND` whether the recipe is missing or belongs to another user. This prevents an authenticated caller from probing whether a given recipe ID exists at all.

### PATCH uses `exclude_unset=True`
`RecipeUpdate.model_dump(exclude_unset=True)` means only fields explicitly included in the JSON body are written. Omitted fields are untouched. This is correct PATCH semantics and avoids accidentally clearing optional fields.

---

## Design Decisions

### `serving_unit` as free text (not an enum)
Serving units vary widely across cuisines and recipe sources — "cup", "bowl", "piece", "gram", "portion", etc. An enum would require maintenance and would reject valid user-entered values. Free text with a sensible default ("portion") covers the use case.

### `user_id` never in the URL
New routes use the `X-User-Id` header, not `/users/{user_id}/...` nesting. The legacy `POST /users/{user_id}/recipes` endpoint is left untouched for now and will be removed in `feature/basic-auth` when JWT auth replaces the header stub.

### Ingredients deferred
Including ingredients in the same import would require resolving ingredient identity, which is a feature of its own. Recipe-level macros (entered or parsed) are stored as-is and will be compared to computed macro totals once ingredients land.

---

## Test Coverage

Tests in `tests/test_recipes.py`. Service layer is mocked via `dependency_overrides` — no database required.

| Test class | What is covered |
|---|---|
| `TestImportRecipe` | Legacy endpoint happy path, missing title (422), wrong UUID (422), all optional fields |
| `TestListPersonalRecipes` | Happy path, empty list, `q` forwarded to service, pagination params, missing header (422), serving fields in response |
| `TestGetPersonalRecipe` | Happy path, 404 not found, 404 wrong owner, invalid UUID (422) |
| `TestUpdatePersonalRecipe` | Happy path, 404, invalid field value (422), empty body valid, serving fields |
| `TestDeletePersonalRecipe` | 204 on success, 404, service called with correct args |
| `TestListCatalogRecipes` | Happy path, `q` forwarded, pagination params, no X-User-Id required |
| `TestGetCatalogRecipe` | Happy path, 404 not found, 404 non-global recipe, invalid UUID (422) |

---

## What Is Explicitly Deferred

- **Ingredient lines on recipes** — `feature/ingredient-library` will add `RecipeIngredient` rows and embed `ingredients[]` in recipe responses.
- **Auth** — `X-User-Id` header replaced by JWT in `feature/basic-auth`. The `get_current_user_id` dependency is the single swap point.
- **Legacy URL cleanup** — `POST /api/v1/users/{user_id}/recipes` removed in `feature/basic-auth`.
- **Instagram / URL import** — out of scope for this branch; `source_type` enum already has slots for it.

