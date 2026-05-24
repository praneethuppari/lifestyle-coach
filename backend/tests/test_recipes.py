import types
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from lifestyle_coach_api.api.dependencies import get_current_user_id
from lifestyle_coach_api.api.routes.recipes import get_recipe_service
from lifestyle_coach_api.core.errors import NotFoundError
from lifestyle_coach_api.main import app
from lifestyle_coach_api.models.recipe import RecipeDifficulty, RecipeSourceType
from lifestyle_coach_api.services.recipes import RecipeService


def _make_recipe(**kwargs) -> types.SimpleNamespace:
    """Build a plain namespace that satisfies RecipeResponse.model_validate().

    Uses SimpleNamespace instead of a real SQLAlchemy Recipe to avoid ORM
    relationship machinery during tests (backref validation fails on non-ORM
    objects assigned to relationship collections).
    """
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "title": "Chicken Tikka Masala",
        "description": None,
        "source_url": None,
        "source_type": RecipeSourceType.manual,
        "source_author": None,
        "is_verified": False,
        "is_global": False,
        "image_url": None,
        "cuisine": "indian",
        "difficulty": None,
        "prep_time_minutes": None,
        "cook_time_minutes": None,
        "servings": None,
        "serving_unit": "portion",
        "serving_weight_g": None,
        "instructions": None,
        "calories": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "fiber_g": None,
        "tags": [],
        "ingredients": [],
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    return types.SimpleNamespace(**{**defaults, **kwargs})


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestImportRecipe:
    def test_imports_recipe_and_returns_201(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)
        mock_service = MagicMock(spec=RecipeService)
        mock_service.import_custom.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service

        response = client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={"title": "Chicken Tikka Masala", "cuisine": "indian"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Chicken Tikka Masala"
        assert body["source_type"] == "manual"
        assert body["is_global"] is False
        assert "id" in body

    def test_returns_422_when_title_is_missing(self, client: TestClient) -> None:
        user_id = uuid.uuid4()

        response = client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={"cuisine": "italian"},
        )

        assert response.status_code == 422

    def test_passes_correct_user_id_to_service(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)
        mock_service = MagicMock(spec=RecipeService)
        mock_service.import_custom.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service

        client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={"title": "My Recipe"},
        )

        mock_service.import_custom.assert_called_once()
        called_user_id = mock_service.import_custom.call_args[0][0]
        assert called_user_id == user_id

    def test_returns_422_when_user_id_is_not_a_uuid(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/users/not-a-uuid/recipes",
            json={"title": "My Recipe"},
        )

        assert response.status_code == 422

    def test_imports_recipe_with_all_optional_fields(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(
            user_id=user_id,
            difficulty=RecipeDifficulty.easy,
            prep_time_minutes=15,
            cook_time_minutes=30,
            servings=4,
            calories=450.0,
            protein_g=35.0,
            carbs_g=40.0,
            fat_g=12.0,
            tags=["high-protein", "indian"],
        )
        mock_service = MagicMock(spec=RecipeService)
        mock_service.import_custom.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service

        response = client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={
                "title": "Chicken Tikka Masala",
                "difficulty": "easy",
                "prep_time_minutes": 15,
                "cook_time_minutes": 30,
                "servings": 4,
                "calories": 450.0,
                "protein_g": 35.0,
                "carbs_g": 40.0,
                "fat_g": 12.0,
                "tags": ["high-protein", "indian"],
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["difficulty"] == "easy"
        assert body["prep_time_minutes"] == 15
        assert body["tags"] == ["high-protein", "indian"]


# ---------------------------------------------------------------------------
# GET /api/v1/recipes  — list personal recipes
# ---------------------------------------------------------------------------


class TestListPersonalRecipes:
    def _setup(self, client: TestClient, user_id: uuid.UUID, result: tuple) -> MagicMock:
        mock_service = MagicMock(spec=RecipeService)
        mock_service.list_personal.return_value = result
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_returns_paginated_list(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)
        self._setup(client, user_id, ([recipe], 1))

        response = client.get("/api/v1/recipes")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert body["page_size"] == 20
        assert len(body["items"]) == 1
        assert body["items"][0]["title"] == recipe.title

    def test_returns_empty_list_when_no_recipes(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        self._setup(client, user_id, ([], 0))

        response = client.get("/api/v1/recipes")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 0
        assert body["items"] == []

    def test_forwards_q_to_service(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id, ([], 0))

        client.get("/api/v1/recipes?q=chicken")

        mock_service.list_personal.assert_called_once_with(user_id, "chicken", 1, 20)

    def test_forwards_pagination_params_to_service(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id, ([], 0))

        client.get("/api/v1/recipes?page=3&page_size=5")

        mock_service.list_personal.assert_called_once_with(user_id, None, 3, 5)

    def test_returns_422_when_x_user_id_header_missing(self, client: TestClient) -> None:
        # Do not override get_current_user_id — test real header parsing
        response = client.get("/api/v1/recipes")

        assert response.status_code == 422

    def test_response_includes_serving_fields(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id, serving_unit="cup", serving_weight_g=240.0)
        self._setup(client, user_id, ([recipe], 1))

        response = client.get("/api/v1/recipes")

        body = response.json()
        assert body["items"][0]["serving_unit"] == "cup"
        assert body["items"][0]["serving_weight_g"] == 240.0


# ---------------------------------------------------------------------------
# GET /api/v1/recipes/{recipe_id}  — personal recipe detail
# ---------------------------------------------------------------------------


class TestGetPersonalRecipe:
    def _setup(self, client: TestClient, user_id: uuid.UUID) -> MagicMock:
        mock_service = MagicMock(spec=RecipeService)
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_returns_recipe(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)
        mock_service = self._setup(client, user_id)
        mock_service.get_personal.return_value = recipe

        response = client.get(f"/api/v1/recipes/{recipe.id}")

        assert response.status_code == 200
        assert response.json()["id"] == str(recipe.id)

    def test_returns_404_when_not_found(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.get_personal.side_effect = NotFoundError(
            detail="Recipe not found.", code="recipe_not_found"
        )

        response = client.get(f"/api/v1/recipes/{recipe_id}")

        assert response.status_code == 404

    def test_returns_404_when_recipe_belongs_to_other_user(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        other_recipe_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.get_personal.side_effect = NotFoundError(
            detail="Recipe not found.", code="recipe_not_found"
        )

        response = client.get(f"/api/v1/recipes/{other_recipe_id}")

        assert response.status_code == 404

    def test_returns_422_for_invalid_recipe_id(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        self._setup(client, user_id)

        response = client.get("/api/v1/recipes/not-a-uuid")

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /api/v1/recipes/{recipe_id}  — partial metadata update
# ---------------------------------------------------------------------------


class TestUpdatePersonalRecipe:
    def _setup(self, client: TestClient, user_id: uuid.UUID) -> MagicMock:
        mock_service = MagicMock(spec=RecipeService)
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_updates_recipe_and_returns_200(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id, title="Updated Title")
        mock_service = self._setup(client, user_id)
        mock_service.update.return_value = recipe

        response = client.patch(
            f"/api/v1/recipes/{recipe.id}",
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_returns_404_when_not_found_or_wrong_owner(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.update.side_effect = NotFoundError(
            detail="Recipe not found.", code="recipe_not_found"
        )

        response = client.patch(f"/api/v1/recipes/{recipe_id}", json={"title": "x"})

        assert response.status_code == 404

    def test_returns_422_for_invalid_field_value(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        self._setup(client, user_id)

        # servings must be >= 1
        response = client.patch(
            f"/api/v1/recipes/{uuid.uuid4()}",
            json={"servings": 0},
        )

        assert response.status_code == 422

    def test_empty_body_is_valid(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)
        mock_service = self._setup(client, user_id)
        mock_service.update.return_value = recipe

        response = client.patch(f"/api/v1/recipes/{recipe.id}", json={})

        assert response.status_code == 200

    def test_updates_serving_fields(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id, serving_unit="cup", serving_weight_g=200.0)
        mock_service = self._setup(client, user_id)
        mock_service.update.return_value = recipe

        response = client.patch(
            f"/api/v1/recipes/{recipe.id}",
            json={"serving_unit": "cup", "serving_weight_g": 200.0},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["serving_unit"] == "cup"
        assert body["serving_weight_g"] == 200.0


# ---------------------------------------------------------------------------
# DELETE /api/v1/recipes/{recipe_id}
# ---------------------------------------------------------------------------


class TestDeletePersonalRecipe:
    def _setup(self, client: TestClient, user_id: uuid.UUID) -> MagicMock:
        mock_service = MagicMock(spec=RecipeService)
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_returns_204_on_success(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.delete.return_value = None

        response = client.delete(f"/api/v1/recipes/{uuid.uuid4()}")

        assert response.status_code == 204
        assert response.content == b""

    def test_returns_404_when_not_found_or_wrong_owner(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.delete.side_effect = NotFoundError(
            detail="Recipe not found.", code="recipe_not_found"
        )

        response = client.delete(f"/api/v1/recipes/{uuid.uuid4()}")

        assert response.status_code == 404

    def test_calls_service_with_correct_args(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        recipe_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.delete.return_value = None

        client.delete(f"/api/v1/recipes/{recipe_id}")

        mock_service.delete.assert_called_once_with(user_id, recipe_id)


# ---------------------------------------------------------------------------
# GET /api/v1/catalog/recipes  — list global catalog
# ---------------------------------------------------------------------------


class TestListCatalogRecipes:
    def _setup(self, client: TestClient, result: tuple) -> MagicMock:
        mock_service = MagicMock(spec=RecipeService)
        mock_service.list_catalog.return_value = result
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        return mock_service

    def test_returns_paginated_list(self, client: TestClient) -> None:
        recipe = _make_recipe(is_global=True, user_id=None)
        self._setup(client, ([recipe], 1))

        response = client.get("/api/v1/catalog/recipes")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert body["page_size"] == 20
        assert len(body["items"]) == 1

    def test_forwards_q_to_service(self, client: TestClient) -> None:
        mock_service = self._setup(client, ([], 0))

        client.get("/api/v1/catalog/recipes?q=pasta")

        mock_service.list_catalog.assert_called_once_with("pasta", 1, 20)

    def test_forwards_pagination_params_to_service(self, client: TestClient) -> None:
        mock_service = self._setup(client, ([], 0))

        client.get("/api/v1/catalog/recipes?page=2&page_size=10")

        mock_service.list_catalog.assert_called_once_with(None, 2, 10)

    def test_does_not_require_x_user_id_header(self, client: TestClient) -> None:
        self._setup(client, ([], 0))

        # No X-User-Id header — catalog is read-only and does not need auth for now
        response = client.get("/api/v1/catalog/recipes")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/catalog/recipes/{recipe_id}  — catalog recipe detail
# ---------------------------------------------------------------------------


class TestGetCatalogRecipe:
    def _setup(self, client: TestClient) -> MagicMock:
        mock_service = MagicMock(spec=RecipeService)
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        return mock_service

    def test_returns_global_recipe(self, client: TestClient) -> None:
        recipe = _make_recipe(is_global=True, user_id=None)
        mock_service = self._setup(client)
        mock_service.get_catalog.return_value = recipe

        response = client.get(f"/api/v1/catalog/recipes/{recipe.id}")

        assert response.status_code == 200
        assert response.json()["id"] == str(recipe.id)
        assert response.json()["is_global"] is True

    def test_returns_404_when_not_found(self, client: TestClient) -> None:
        mock_service = self._setup(client)
        mock_service.get_catalog.side_effect = NotFoundError(
            detail="Catalog recipe not found.", code="recipe_not_found"
        )

        response = client.get(f"/api/v1/catalog/recipes/{uuid.uuid4()}")

        assert response.status_code == 404

    def test_returns_404_when_recipe_is_not_global(self, client: TestClient) -> None:
        mock_service = self._setup(client)
        # Service enforces is_global check and raises NotFoundError
        mock_service.get_catalog.side_effect = NotFoundError(
            detail="Catalog recipe not found.", code="recipe_not_found"
        )

        response = client.get(f"/api/v1/catalog/recipes/{uuid.uuid4()}")

        assert response.status_code == 404

    def test_returns_422_for_invalid_recipe_id(self, client: TestClient) -> None:
        self._setup(client)

        response = client.get("/api/v1/catalog/recipes/not-a-uuid")

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Recipe + ingredient integration tests
# ---------------------------------------------------------------------------


def _make_recipe_ingredient(ingredient_id: uuid.UUID, **kwargs):
    """Build a plain namespace that looks like a RecipeIngredient ORM row."""
    import types

    ingredient = types.SimpleNamespace(
        id=kwargs.get("ingredient_id", uuid.uuid4()),
        name=kwargs.get("name", "Chicken breast"),
        brand=kwargs.get("brand", None),
    )
    return types.SimpleNamespace(
        ingredient_id=ingredient_id,
        quantity=kwargs.get("quantity", 200.0),
        unit=kwargs.get("unit", "g"),
        preparation=kwargs.get("preparation", None),
        notes=kwargs.get("notes", None),
        order=kwargs.get("order", 0),
        ingredient=ingredient,
    )


class TestRecipeWithIngredients:
    def test_import_recipe_with_ingredients_returns_embedded_list(
        self, client: TestClient
    ) -> None:
        user_id = uuid.uuid4()
        ingredient_id = uuid.uuid4()
        recipe_id = uuid.uuid4()
        ri = _make_recipe_ingredient(ingredient_id, name="Chicken breast")
        recipe = _make_recipe(id=recipe_id, user_id=user_id, ingredients=[ri])

        mock_service = MagicMock(spec=RecipeService)
        mock_service.import_custom.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        response = client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={
                "title": "Chicken Salad",
                "ingredients": [
                    {"ingredient_id": str(ingredient_id), "quantity": 200, "unit": "g"}
                ],
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert len(body["ingredients"]) == 1
        assert body["ingredients"][0]["ingredient"]["name"] == "Chicken breast"
        assert body["ingredients"][0]["quantity"] == 200.0
        assert body["ingredients"][0]["unit"] == "g"

    def test_import_recipe_passes_ingredient_items_to_service(
        self, client: TestClient
    ) -> None:
        user_id = uuid.uuid4()
        ingredient_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)

        mock_service = MagicMock(spec=RecipeService)
        mock_service.import_custom.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={
                "title": "Chicken Salad",
                "ingredients": [
                    {"ingredient_id": str(ingredient_id), "quantity": 200, "unit": "g"}
                ],
            },
        )

        mock_service.import_custom.assert_called_once()
        data = mock_service.import_custom.call_args[0][1]
        assert len(data.ingredients) == 1
        assert data.ingredients[0].ingredient_id == ingredient_id

    def test_recipe_response_includes_empty_ingredients_by_default(
        self, client: TestClient
    ) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id, recipe_ingredients=[])

        mock_service = MagicMock(spec=RecipeService)
        mock_service.import_custom.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        response = client.post(
            f"/api/v1/users/{user_id}/recipes",
            json={"title": "Simple Recipe"},
        )

        assert response.status_code == 201
        assert response.json()["ingredients"] == []

    def test_update_recipe_passes_ingredient_replacement_to_service(
        self, client: TestClient
    ) -> None:
        user_id = uuid.uuid4()
        ingredient_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)

        mock_service = MagicMock(spec=RecipeService)
        mock_service.update.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        response = client.patch(
            f"/api/v1/recipes/{recipe.id}",
            json={
                "ingredients": [
                    {"ingredient_id": str(ingredient_id), "quantity": 150, "unit": "ml"}
                ]
            },
        )

        assert response.status_code == 200
        mock_service.update.assert_called_once()
        data = mock_service.update.call_args[0][2]
        assert data.ingredients is not None
        assert len(data.ingredients) == 1
        assert data.ingredients[0].ingredient_id == ingredient_id

    def test_update_without_ingredients_key_leaves_ingredients_unset(
        self, client: TestClient
    ) -> None:
        user_id = uuid.uuid4()
        recipe = _make_recipe(user_id=user_id)

        mock_service = MagicMock(spec=RecipeService)
        mock_service.update.return_value = recipe
        app.dependency_overrides[get_recipe_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        client.patch(f"/api/v1/recipes/{recipe.id}", json={"title": "New Title"})

        data = mock_service.update.call_args[0][2]
        assert data.ingredients is None

