from datetime import datetime
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.config import settings


def test_jobs_accepts_known_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    class _AsyncClientSuccess:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientSuccess":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def post(self, *_: Any, **kwargs: Any) -> httpx.Response:
            calls.append({"payload": kwargs.get("json")})
            request = httpx.Request("POST", "http://test")
            return httpx.Response(status_code=202, request=request)

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientSuccess)

    payload = {
        "job_id": "job-123",
        "client_id": "client-abc",
        "workflow_key": "tiktok_live_helper",
        "inputs": {"foo": "bar"},
        "callback_url": "https://example.com/callback",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs", json=payload)

    assert response.status_code == 202

    data = response.json()
    assert data["job_id"] == "job-123"
    assert data["status"] == "pending"
    assert data["message"] == "accepted"
    assert datetime.fromisoformat(data["accepted_at"])
    assert len(calls) == 1


def test_jobs_dispatch_failure_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class _AsyncClientFailure:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientFailure":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def post(self, *_: Any, **__: Any) -> httpx.Response:
            raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientFailure)

    payload = {
        "job_id": "job-456",
        "client_id": "client-xyz",
        "workflow_key": "tiktok_live_helper",
        "inputs": {"foo": "bar"},
        "callback_url": "https://example.com/callback",
    }

    with caplog.at_level("ERROR"):
        with TestClient(app) as client:
            response = client.post("/v1/jobs", json=payload)

    assert response.status_code == 202
    assert any("n8n dispatch failed" in record.message for record in caplog.records)


def test_jobs_rejects_unknown_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    class _AsyncClientSuccess:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientSuccess":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def post(self, *_: Any, **__: Any) -> httpx.Response:
            return httpx.Response(status_code=202)

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientSuccess)

    payload = {
        "job_id": "job-123",
        "client_id": "client-abc",
        "workflow_key": "missing_workflow",
        "inputs": {"foo": "bar"},
        "callback_url": "https://example.com/callback",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown workflow_key"


def test_cancel_deactivates_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "n8n_api_key", "dummy-key")
    monkeypatch.setattr(settings, "n8n_api_base_url", "http://n8n:5678/api/v1")

    calls: list[dict[str, object]] = []

    class _AsyncClientDeactivate:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientDeactivate":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def get(self, url: str, **__: Any) -> httpx.Response:
            request = httpx.Request("GET", url)
            return httpx.Response(
                status_code=200,
                request=request,
                json={"data": [{"id": 7, "name": "tiktok_live_helper", "active": True}]},
            )

        async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
            calls.append({"url": url, "payload": kwargs.get("json")})
            request = httpx.Request("PATCH", url)
            return httpx.Response(status_code=200, request=request, json={"id": 7, "active": False})

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientDeactivate)

    payload = {
        "client_id": "client-123",
        "workflow_key": "tiktok_live_helper",
        "reason": "ops kill-switch",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs/job-999/cancel", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-999"
    assert data["status"] == "cancelled"
    assert data["workflow_deactivated"] is True
    assert calls and calls[0]["payload"] == {"active": False}


def test_cancel_matches_display_name_slug(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "n8n_api_key", "dummy-key")

    class _AsyncClientDeactivate:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientDeactivate":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def get(self, url: str, **__: Any) -> httpx.Response:
            request = httpx.Request("GET", url)
            return httpx.Response(
                status_code=200,
                request=request,
                json={"data": [{"id": 9, "displayName": "TikTok Live Helper", "active": True}]},
            )

        async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
            request = httpx.Request("PATCH", url)
            return httpx.Response(status_code=200, request=request, json={"id": 9, "active": False})

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientDeactivate)

    payload = {
        "client_id": "client-321",
        "workflow_key": "tiktok_live_helper",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs/job-111/cancel", json=payload)

    assert response.status_code == 200
    assert response.json()["workflow_deactivated"] is True


def test_cancel_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "n8n_api_key", None)

    payload = {
        "client_id": "client-789",
        "workflow_key": "tiktok_live_helper",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs/job-1/cancel", json=payload)

    assert response.status_code == 503
    assert "N8N_API_KEY" in response.json()["detail"]


def test_cancel_404_when_workflow_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "n8n_api_key", "dummy-key")

    class _AsyncClientNoMatch:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientNoMatch":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def get(self, url: str, **__: Any) -> httpx.Response:
            request = httpx.Request("GET", url)
            return httpx.Response(status_code=200, request=request, json={"data": []})

        async def patch(self, *_: Any, **__: Any) -> httpx.Response:
            request = httpx.Request("PATCH", "http://test")
            return httpx.Response(status_code=404, request=request)

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientNoMatch)

    payload = {
        "client_id": "client-456",
        "workflow_key": "tiktok_live_helper",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs/job-2/cancel", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow not found in n8n"


def test_cancel_handles_n8n_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "n8n_api_key", "dummy-key")

    class _AsyncClientFailure:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_AsyncClientFailure":
            return self

        async def __aexit__(self, *exc_info: object) -> None:
            return None

        async def get(self, url: str, **__: Any) -> httpx.Response:
            request = httpx.Request("GET", url)
            response = httpx.Response(status_code=500, request=request)
            response.raise_for_status()
            return response

    monkeypatch.setattr(httpx, "AsyncClient", _AsyncClientFailure)

    payload = {
        "client_id": "client-555",
        "workflow_key": "tiktok_live_helper",
    }

    with TestClient(app) as client:
        response = client.post("/v1/jobs/job-3/cancel", json=payload)

    assert response.status_code == 502
    assert response.json()["detail"] == "Failed to deactivate workflow via n8n"
