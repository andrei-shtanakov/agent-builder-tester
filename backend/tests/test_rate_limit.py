"""Tests for rate limiting functionality."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_rate_limit_allows_requests_within_limit(client: TestClient) -> None:
    """Test that requests within the rate limit are allowed."""
    # Make multiple requests to the root endpoint (no database required)
    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200


def test_rate_limit_health_endpoint(client: TestClient) -> None:
    """Test that health check endpoint is accessible."""
    # Health endpoint should work fine
    for _ in range(5):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_rate_limiter_is_configured(client: TestClient) -> None:
    """Test that rate limiter is properly configured in the app."""
    # Verify the app has the rate limiter state
    assert hasattr(app.state, "limiter")
    assert app.state.limiter is not None


def test_rate_limit_config_settings() -> None:
    """Test that rate limit settings are properly configured."""
    from backend.app.config import settings

    assert settings.rate_limit_enabled is not None
    assert settings.rate_limit_default is not None
    assert settings.rate_limit_strict is not None
    assert isinstance(settings.rate_limit_default, str)
    assert "/" in settings.rate_limit_default  # Should be in format "X/minute"
