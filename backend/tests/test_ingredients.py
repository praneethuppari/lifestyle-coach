import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from lifestyle_coach_api.api.dependencies import get_current_user_id
from lifestyle_coach_api.api.routes.ingredients import get_ingredient_service
from lifestyle_coach_api.core.errors import NotFoundError
from lifestyle_coach_api.main import app
from lifestyle_coach_api.models.ingredient import Ingredient
from lifestyle_coach_api.services.ingredients import IngredientService


def _make_ingredient(**kwargs) -> Ingredient:
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "name": "Chicken breast",
        "brand": None,
        "barcode": None,
        "is_global": False,
        "source": None,
        "source_id": None,
        "serving_size_amount": None,
        "serving_size_unit": None,
        "calories_per_100g": None,
        "protein_per_100g": None,
        "carbs_per_100g": None,
        "fat_per_100g": None,
        "fiber_per_100g": None,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    return Ingredient(**{**defaults, **kwargs})


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/v1/ingredients
# ---------------------------------------------------------------------------


class TestImportIngredient:
    def test_creates_ingredient_and_returns_201(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(user_id=user_id)
        mock_service = MagicMock(spec=IngredientService)
        mock_service.import_custom.return_value = ingredient
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        response = client.post("/api/v1/ingredients", json={"name": "Chicken breast"})

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Chicken breast"
        assert body["is_global"] is False
        assert "id" in body

    def test_returns_422_when_name_is_missing(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        response = client.post("/api/v1/ingredients", json={"brand": "Tyson"})

        assert response.status_code == 422

    def test_returns_422_when_x_user_id_header_missing(self, client: TestClient) -> None:
        response = client.post("/api/v1/ingredients", json={"name": "Chicken breast"})

        assert response.status_code == 422

    def test_passes_correct_user_id_to_service(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(user_id=user_id)
        mock_service = MagicMock(spec=IngredientService)
        mock_service.import_custom.return_value = ingredient
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        client.post("/api/v1/ingredients", json={"name": "Oats"})

        called_user_id = mock_service.import_custom.call_args[0][0]
        assert called_user_id == user_id

    def test_creates_ingredient_with_nutrition_fields(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(
            user_id=user_id,
            calories_per_100g=165.0,
            protein_per_100g=31.0,
            carbs_per_100g=0.0,
            fat_per_100g=3.6,
        )
        mock_service = MagicMock(spec=IngredientService)
        mock_service.import_custom.return_value = ingredient
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id

        response = client.post(
            "/api/v1/ingredients",
            json={
                "name": "Chicken breast",
                "calories_per_100g": 165.0,
                "protein_per_100g": 31.0,
                "carbs_per_100g": 0.0,
                "fat_per_100g": 3.6,
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["calories_per_100g"] == 165.0
        assert body["protein_per_100g"] == 31.0


# ---------------------------------------------------------------------------
# GET /api/v1/ingredients  — list personal ingredient library
# ---------------------------------------------------------------------------


class TestListPersonalIngredients:
    def _setup(
        self, client: TestClient, user_id: uuid.UUID, result: tuple
    ) -> MagicMock:
        mock_service = MagicMock(spec=IngredientService)
        mock_service.list_personal.return_value = result
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_returns_paginated_list(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(user_id=user_id)
        self._setup(client, user_id, ([ingredient], 1))

        response = client.get("/api/v1/ingredients")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert body["page_size"] == 20
        assert len(body["items"]) == 1
        assert body["items"][0]["name"] == ingredient.name

    def test_returns_empty_list_when_library_is_empty(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        self._setup(client, user_id, ([], 0))

        response = client.get("/api/v1/ingredients")

        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_passes_query_and_pagination_to_service(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id, ([], 0))

        client.get("/api/v1/ingredients?q=chicken&page=2&page_size=10")

        mock_service.list_personal.assert_called_once_with(user_id, "chicken", 2, 10)

    def test_returns_422_when_x_user_id_header_missing(self, client: TestClient) -> None:
        response = client.get("/api/v1/ingredients")

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/ingredients/{ingredient_id}
# ---------------------------------------------------------------------------


class TestGetPersonalIngredient:
    def _setup(self, client: TestClient, user_id: uuid.UUID) -> MagicMock:
        mock_service = MagicMock(spec=IngredientService)
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_returns_ingredient(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(user_id=user_id)
        mock_service = self._setup(client, user_id)
        mock_service.get_personal.return_value = ingredient

        response = client.get(f"/api/v1/ingredients/{ingredient.id}")

        assert response.status_code == 200
        assert response.json()["id"] == str(ingredient.id)
        assert response.json()["name"] == ingredient.name

    def test_returns_404_when_not_found(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.get_personal.side_effect = NotFoundError(
            detail="Ingredient not found.", code="ingredient_not_found"
        )

        response = client.get(f"/api/v1/ingredients/{uuid.uuid4()}")

        assert response.status_code == 404

    def test_returns_422_for_invalid_ingredient_id(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        self._setup(client, user_id)

        response = client.get("/api/v1/ingredients/not-a-uuid")

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /api/v1/ingredients/{ingredient_id}
# ---------------------------------------------------------------------------


class TestUpdateIngredient:
    def _setup(self, client: TestClient, user_id: uuid.UUID) -> MagicMock:
        mock_service = MagicMock(spec=IngredientService)
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_updates_ingredient_and_returns_200(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(user_id=user_id, name="Brown rice")
        mock_service = self._setup(client, user_id)
        mock_service.update.return_value = ingredient

        response = client.patch(
            f"/api/v1/ingredients/{ingredient.id}", json={"name": "Brown rice"}
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Brown rice"

    def test_returns_404_when_not_found(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.update.side_effect = NotFoundError(
            detail="Ingredient not found.", code="ingredient_not_found"
        )

        response = client.patch(
            f"/api/v1/ingredients/{uuid.uuid4()}", json={"name": "New Name"}
        )

        assert response.status_code == 404

    def test_passes_only_set_fields_to_service(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        ingredient = _make_ingredient(user_id=user_id)
        mock_service = self._setup(client, user_id)
        mock_service.update.return_value = ingredient

        client.patch(
            f"/api/v1/ingredients/{ingredient.id}", json={"calories_per_100g": 120.0}
        )

        data = mock_service.update.call_args[0][2]
        assert "calories_per_100g" in data.model_fields_set
        assert "name" not in data.model_fields_set


# ---------------------------------------------------------------------------
# DELETE /api/v1/ingredients/{ingredient_id}
# ---------------------------------------------------------------------------


class TestDeleteIngredient:
    def _setup(self, client: TestClient, user_id: uuid.UUID) -> MagicMock:
        mock_service = MagicMock(spec=IngredientService)
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return mock_service

    def test_deletes_ingredient_and_returns_204(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)

        response = client.delete(f"/api/v1/ingredients/{uuid.uuid4()}")

        assert response.status_code == 204
        mock_service.delete.assert_called_once()

    def test_returns_404_when_not_found(self, client: TestClient) -> None:
        user_id = uuid.uuid4()
        mock_service = self._setup(client, user_id)
        mock_service.delete.side_effect = NotFoundError(
            detail="Ingredient not found.", code="ingredient_not_found"
        )

        response = client.delete(f"/api/v1/ingredients/{uuid.uuid4()}")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/catalog/ingredients
# ---------------------------------------------------------------------------


class TestListCatalogIngredients:
    def _setup(self, client: TestClient, result: tuple) -> MagicMock:
        mock_service = MagicMock(spec=IngredientService)
        mock_service.list_catalog.return_value = result
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        return mock_service

    def test_returns_paginated_catalog(self, client: TestClient) -> None:
        ingredient = _make_ingredient(is_global=True, user_id=None)
        self._setup(client, ([ingredient], 1))

        response = client.get("/api/v1/catalog/ingredients")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["name"] == ingredient.name

    def test_returns_empty_list_when_catalog_is_empty(self, client: TestClient) -> None:
        self._setup(client, ([], 0))

        response = client.get("/api/v1/catalog/ingredients")

        assert response.status_code == 200
        assert response.json()["items"] == []

    def test_passes_query_and_pagination_to_service(self, client: TestClient) -> None:
        mock_service = self._setup(client, ([], 0))

        client.get("/api/v1/catalog/ingredients?q=oats&page=3&page_size=5")

        mock_service.list_catalog.assert_called_once_with("oats", 3, 5)

    def test_does_not_require_auth_header(self, client: TestClient) -> None:
        """Catalog is read-only and does not depend on user identity."""
        self._setup(client, ([], 0))

        response = client.get("/api/v1/catalog/ingredients")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/v1/catalog/ingredients/{ingredient_id}
# ---------------------------------------------------------------------------


class TestGetCatalogIngredient:
    def _setup(self, client: TestClient) -> MagicMock:
        mock_service = MagicMock(spec=IngredientService)
        app.dependency_overrides[get_ingredient_service] = lambda: mock_service
        return mock_service

    def test_returns_global_ingredient(self, client: TestClient) -> None:
        ingredient = _make_ingredient(is_global=True, user_id=None)
        mock_service = self._setup(client)
        mock_service.get_catalog.return_value = ingredient

        response = client.get(f"/api/v1/catalog/ingredients/{ingredient.id}")

        assert response.status_code == 200
        assert response.json()["id"] == str(ingredient.id)
        assert response.json()["is_global"] is True

    def test_returns_404_when_not_found(self, client: TestClient) -> None:
        mock_service = self._setup(client)
        mock_service.get_catalog.side_effect = NotFoundError(
            detail="Catalog ingredient not found.", code="ingredient_not_found"
        )

        response = client.get(f"/api/v1/catalog/ingredients/{uuid.uuid4()}")

        assert response.status_code == 404

    def test_returns_422_for_invalid_ingredient_id(self, client: TestClient) -> None:
        self._setup(client)

        response = client.get("/api/v1/catalog/ingredients/not-a-uuid")

        assert response.status_code == 422
