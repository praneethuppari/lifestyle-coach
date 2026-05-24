import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from lifestyle_coach_api.api.routes.users import get_user_service
from lifestyle_coach_api.core.errors import ConflictError
from lifestyle_coach_api.main import app
from lifestyle_coach_api.models.user import User
from lifestyle_coach_api.services.users import UserService


def _make_user(**kwargs) -> User:
    defaults = {
        "id": uuid.uuid4(),
        "email": "alice@example.com",
        "display_name": "Alice",
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    return User(**{**defaults, **kwargs})


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRegisterUser:
    def test_creates_user_and_returns_201(self, client: TestClient) -> None:
        user = _make_user()
        mock_service = MagicMock(spec=UserService)
        mock_service.create.return_value = user
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post(
            "/api/v1/users",
            json={"email": "alice@example.com", "display_name": "Alice"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "alice@example.com"
        assert body["display_name"] == "Alice"
        assert "id" in body
        assert "created_at" in body

    def test_returns_409_when_email_already_exists(self, client: TestClient) -> None:
        mock_service = MagicMock(spec=UserService)
        mock_service.create.side_effect = ConflictError(
            detail="A user with email 'alice@example.com' already exists.",
            code="USER_ALREADY_EXISTS",
        )
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post("/api/v1/users", json={"email": "alice@example.com"})

        assert response.status_code == 409
        body = response.json()
        assert body["code"] == "USER_ALREADY_EXISTS"
        assert body["status"] == 409
        assert body["title"] == "Conflict"
        assert "already exists" in body["detail"]

    def test_returns_422_when_email_is_missing(self, client: TestClient) -> None:
        response = client.post("/api/v1/users", json={"display_name": "Alice"})

        assert response.status_code == 422

    def test_returns_422_when_email_is_invalid(self, client: TestClient) -> None:
        response = client.post("/api/v1/users", json={"email": "not-an-email"})

        assert response.status_code == 422

    def test_creates_user_without_display_name(self, client: TestClient) -> None:
        user = _make_user(display_name=None)
        mock_service = MagicMock(spec=UserService)
        mock_service.create.return_value = user
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post("/api/v1/users", json={"email": "alice@example.com"})

        assert response.status_code == 201
        assert response.json()["display_name"] is None
