import hashlib
import hmac
import json
from typing import Any

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.config import settings


def _build_signature(secret: str, body: str) -> str:
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


def test_callbacks_accept_without_secret(caplog: Any) -> None:
    payload = {
        "job_id": "job-1",
        "status": "success",
        "outputs": {"result": True},
    }

    with caplog.at_level("WARNING"):
        with TestClient(app) as client:
            response = client.post("/v1/callbacks/n8n", json=payload)

    assert response.status_code == 200
    assert any("signature not validated" in record.message for record in caplog.records)


def test_callbacks_rejects_invalid_signature(monkeypatch: Any) -> None:
    monkeypatch.setattr(settings, "callback_signing_secret", "topsecret")

    payload = {
        "job_id": "job-2",
        "status": "failed",
        "outputs": {},
    }
    body = json.dumps(payload, separators=(",", ":"))

    headers = {
        "Content-Type": "application/json",
        "X-Callback-Signature": "bad-signature",
    }

    with TestClient(app) as client:
        response = client.post("/v1/callbacks/n8n", data=body, headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid callback signature"


def test_callbacks_requires_signature_when_secret_set(monkeypatch: Any) -> None:
    monkeypatch.setattr(settings, "callback_signing_secret", "topsecret")

    payload = {
        "job_id": "job-4",
        "status": "success",
        "outputs": {},
    }

    with TestClient(app) as client:
        response = client.post("/v1/callbacks/n8n", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing callback signature"


def test_callbacks_accepts_valid_signature(monkeypatch: Any) -> None:
    monkeypatch.setattr(settings, "callback_signing_secret", "topsecret")

    payload = {
        "job_id": "job-3",
        "status": "success",
        "outputs": {"value": 42},
        "execution_id": "exec-123",
    }
    body = json.dumps(payload, separators=(",", ":"))
    signature = _build_signature("topsecret", body)

    headers = {
        "Content-Type": "application/json",
        "X-Callback-Signature": signature,
    }

    with TestClient(app) as client:
        response = client.post("/v1/callbacks/n8n", data=body, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_callbacks_persist_audit_log(monkeypatch: Any, tmp_path: Any) -> None:
    db_path = tmp_path / "audit.db"
    monkeypatch.setattr(settings, "audit_db_path", str(db_path))

    payload = {
        "job_id": "job-5",
        "status": "success",
        "outputs": {"value": 7},
        "audit": [
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "action": "run",
                "node_name": "node-1",
                "details": {"step": 1},
                "duration_ms": 12,
            }
        ],
        "execution_id": "exec-5",
    }

    with TestClient(app) as client:
        response = client.post("/v1/callbacks/n8n", json=payload)

    assert response.status_code == 200

    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT payload_json FROM audit_logs").fetchall()
    finally:
        conn.close()

    assert len(rows) == 1
    record = json.loads(rows[0][0])
    assert record["job_id"] == payload["job_id"]
    assert record["status"] == payload["status"]
    assert record["audit"][0]["node_name"] == "node-1"
    assert "stored_at" in record
