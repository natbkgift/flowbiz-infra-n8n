from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_meta_returns_200():
    """Test that meta endpoint returns 200 status code."""
    response = client.get("/v1/meta")
    assert response.status_code == 200


def test_meta_response_structure():
    """Test that meta endpoint returns correct JSON structure."""
    response = client.get("/v1/meta")
    data = response.json()

    assert "service" in data
    assert "environment" in data
    assert "version" in data
    assert "build_sha" in data


def test_meta_service_name():
    """Test that meta endpoint returns service name."""
    response = client.get("/v1/meta")
    data = response.json()

    assert data["service"] == "flowbiz-template-service"


def test_meta_environment():
    """Test that meta endpoint returns environment."""
    response = client.get("/v1/meta")
    data = response.json()

    assert data["environment"] in ["dev", "prod"]


def test_meta_version():
    """Test that meta endpoint returns version."""
    response = client.get("/v1/meta")
    data = response.json()

    assert data["version"] == "0.1.0"


def test_meta_build_sha():
    """Test that meta endpoint returns build_sha."""
    response = client.get("/v1/meta")
    data = response.json()

    assert "build_sha" in data
    assert isinstance(data["build_sha"], str)
