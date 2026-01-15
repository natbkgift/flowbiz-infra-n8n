from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from packages.core.schemas.callback import AuditEntry, CallbackStatus, JobCallback
from packages.core.schemas.job import JobRequest, JobResponse, JobStatus


def test_job_request_defaults() -> None:
    req = JobRequest(
        job_id="job-123",
        client_id="client-abc",
        workflow_key="wf-key",
        inputs={"foo": "bar"},
        callback_url="https://example.com/callback",
    )

    assert req.priority == 5
    assert req.timeout_seconds == 300
    assert req.metadata == {}


@pytest.mark.parametrize(
    ("priority", "is_valid"),
    [
        (0, False),
        (11, False),
        (1, True),
        (10, True),
    ],
)
def test_job_request_priority_bounds(priority: int, is_valid: bool) -> None:
    payload = {
        "job_id": "job-123",
        "client_id": "client-abc",
        "workflow_key": "wf-key",
        "inputs": {},
        "callback_url": "https://example.com/callback",
        "priority": priority,
    }

    if is_valid:
        req = JobRequest(**payload)
        assert req.priority == priority
    else:
        with pytest.raises(ValidationError):
            JobRequest(**payload)


def test_job_request_timeout_seconds_invalid() -> None:
    with pytest.raises(ValidationError):
        JobRequest(
            job_id="job-123",
            client_id="client-abc",
            workflow_key="wf-key",
            inputs={},
            callback_url="https://example.com/callback",
            timeout_seconds=0,
        )


def test_job_request_id_fields_require_value() -> None:
    with pytest.raises(ValidationError):
        JobRequest(
            job_id="",
            client_id="client-abc",
            workflow_key="wf-key",
            inputs={},
            callback_url="https://example.com/callback",
        )


def test_job_response_status_enum() -> None:
    resp = JobResponse(job_id="job-123", status=JobStatus.PENDING)
    assert resp.status is JobStatus.PENDING


def test_job_callback_with_audit_entries() -> None:
    started = datetime(2024, 1, 1, tzinfo=timezone.utc)
    completed = datetime(2024, 1, 1, tzinfo=timezone.utc)
    audit = [
        AuditEntry(
            timestamp=started,
            action="invoke",
            node_name="start",
            details={"step": 1},
            duration_ms=10,
        )
    ]

    cb = JobCallback(
        job_id="job-123",
        status=CallbackStatus.SUCCESS,
        outputs={"result": True},
        audit=audit,
        started_at=started,
        completed_at=completed,
        execution_id="exec-1",
    )

    assert cb.audit[0].node_name == "start"
    assert cb.status is CallbackStatus.SUCCESS
