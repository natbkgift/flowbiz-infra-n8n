from datetime import datetime
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app


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
        "workflow_key": "example_workflow",
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


def test_jobs_dispatch_failure_logs(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
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
        "workflow_key": "example_workflow",
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
