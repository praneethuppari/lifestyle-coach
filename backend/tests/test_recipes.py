import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from lifestyle_coach_api.api.routes.recipes import get_recipe_service
from lifestyle_coach_api.main import app
from lifestyle_coach_api.models.recipe import Recipe, RecipeDifficulty, RecipeSourceType
from lifestyle_coach_api.services.recipes import RecipeService


def _make_recipe(**kwargs) -> Recipe:
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
        "instructions": None,
        "calories": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "fiber_g": None,
        "tags": [],
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    return Recipe(**{**defaults, **kwargs})


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
