import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from lifestyle_coach_api.api.routes.auth import get_user_service
from lifestyle_coach_api.api.routes.recipes import get_recipe_service
from lifestyle_coach_api.core.config import get_settings
from lifestyle_coach_api.core.errors import ConflictError
from lifestyle_coach_api.core.security import create_access_token
from lifestyle_coach_api.main import app
from lifestyle_coach_api.services.users import UserService


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register
# ---------------------------------------------------------------------------


class TestRegister:
    def test_returns_201_with_access_token(self, client: TestClient) -> None:
        fake_token = "fake.jwt.token"
        mock_service = MagicMock(spec=UserService)
        mock_service.register.return_value = fake_token
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "alice@example.com",
                "password": "securepassword",
                "display_name": "Alice",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["access_token"] == fake_token
        assert body["token_type"] == "bearer"

    def test_returns_409_when_email_already_registered(self, client: TestClient) -> None:
        mock_service = MagicMock(spec=UserService)
        mock_service.register.side_effect = ConflictError(
            detail="A user with email 'alice@example.com' already exists.",
            code="USER_ALREADY_EXISTS",
        )
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post(
            "/api/v1/auth/register",
            json={"email": "alice@example.com", "password": "securepassword"},
        )

        assert response.status_code == 409
        body = response.json()
        assert body["code"] == "USER_ALREADY_EXISTS"

    def test_returns_422_when_password_too_short(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "alice@example.com", "password": "short"},
        )

        assert response.status_code == 422

    def test_returns_422_when_email_invalid(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "securepassword"},
        )

        assert response.status_code == 422

    def test_returns_422_when_email_missing(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/register",
            json={"password": "securepassword"},
        )

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------


class TestLogin:
    def test_returns_200_with_access_token(self, client: TestClient) -> None:
        fake_token = "fake.jwt.token"
        mock_service = MagicMock(spec=UserService)
        mock_service.authenticate.return_value = fake_token
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post(
            "/api/v1/auth/login",
            data={"username": "alice@example.com", "password": "securepassword"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == fake_token
        assert body["token_type"] == "bearer"

    def test_returns_401_when_credentials_invalid(self, client: TestClient) -> None:
        mock_service = MagicMock(spec=UserService)
        mock_service.authenticate.return_value = None
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.post(
            "/api/v1/auth/login",
            data={"username": "alice@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"

    def test_passes_email_and_password_to_service(self, client: TestClient) -> None:
        mock_service = MagicMock(spec=UserService)
        mock_service.authenticate.return_value = "token"
        app.dependency_overrides[get_user_service] = lambda: mock_service

        client.post(
            "/api/v1/auth/login",
            data={"username": "alice@example.com", "password": "securepassword"},
        )

        mock_service.authenticate.assert_called_once()
        call_kwargs = mock_service.authenticate.call_args.kwargs
        assert call_kwargs["email"] == "alice@example.com"
        assert call_kwargs["password"] == "securepassword"


# ---------------------------------------------------------------------------
# JWT verification on protected routes
# ---------------------------------------------------------------------------


class TestJWTProtection:
    def test_returns_401_when_no_token_provided(self, client: TestClient) -> None:
        response = client.get("/api/v1/recipes")

        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"

    def test_returns_401_when_token_is_invalid(self, client: TestClient) -> None:
        response = client.get(
            "/api/v1/recipes",
            headers={"Authorization": "Bearer not.a.valid.token"},
        )

        assert response.status_code == 401

    def test_accepts_valid_token(self, client: TestClient) -> None:
        """A real signed token passes the dependency and reaches the service."""
        settings = get_settings()
        user_id = uuid.uuid4()
        token = create_access_token(user_id, settings.secret_key, expire_minutes=30)

        from lifestyle_coach_api.services.recipes import RecipeService as _RS

        mock_service = MagicMock(spec=_RS)
        mock_service.list_personal.return_value = ([], 0)
        app.dependency_overrides[get_recipe_service] = lambda: mock_service

        response = client.get(
            "/api/v1/recipes",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
