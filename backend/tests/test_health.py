import pytest
from fastapi.testclient import TestClient

from lifestyle_coach_api.core.config import Settings, get_settings
from lifestyle_coach_api.main import app


@pytest.fixture
def client() -> TestClient:
    def override_settings() -> Settings:
        return Settings(environment="test")

    app.dependency_overrides[get_settings] = override_settings
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check_returns_service_metadata(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "Lifestyle Coach API",
        "environment": "test",
        "version": "0.1.0",
    }
