from datetime import datetime
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


async def _mock_post_success(*_: Any, **__: Any) -> httpx.Response:
    return httpx.Response(status_code=202)


def test_jobs_accepts_known_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx.AsyncClient, "post", _mock_post_success)

    payload = {
        "job_id": "job-123",
        "client_id": "client-abc",
        "workflow_key": "example_workflow",
        "inputs": {"foo": "bar"},
        "callback_url": "https://example.com/callback",
    }

    response = client.post("/v1/jobs", json=payload)
    assert response.status_code == 202

    data = response.json()
    assert data["job_id"] == "job-123"
    assert data["status"] == "pending"
    assert data["message"] == "accepted"
    assert datetime.fromisoformat(data["accepted_at"])


def test_jobs_rejects_unknown_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx.AsyncClient, "post", _mock_post_success)

    payload = {
        "job_id": "job-123",
        "client_id": "client-abc",
        "workflow_key": "missing_workflow",
        "inputs": {"foo": "bar"},
        "callback_url": "https://example.com/callback",
    }

    response = client.post("/v1/jobs", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown workflow_key"
