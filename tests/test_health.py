from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Test that health check returns 200 status code."""
    response = client.get("/healthz")
    assert response.status_code == 200


def test_health_check_response_structure():
    """Test that health check returns correct JSON structure."""
    response = client.get("/healthz")
    data = response.json()

    assert "status" in data
    assert "service" in data
    assert "version" in data


def test_health_check_status_ok():
    """Test that health check returns ok status."""
    response = client.get("/healthz")
    data = response.json()

    assert data["status"] == "ok"


def test_health_check_service_name():
    """Test that health check returns service name."""
    response = client.get("/healthz")
    data = response.json()

    assert data["service"] == "flowbiz-template-service"


def test_health_check_version():
    """Test that health check returns version."""
    response = client.get("/healthz")
    data = response.json()

    assert data["version"] == "0.1.0"
