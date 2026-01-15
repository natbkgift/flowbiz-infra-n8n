from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class JobStatus(StrEnum):
    """Lifecycle states for a job."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobRequest(BaseModel):
    """Inbound request payload for creating a job."""

    job_id: str = Field(min_length=1)
    client_id: str = Field(min_length=1)
    workflow_key: str = Field(min_length=1)
    inputs: dict[str, Any]
    callback_url: HttpUrl
    priority: int = Field(default=5, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = dict(extra="forbid")


class JobResponse(BaseModel):
    """Synchronous acknowledgement for a job request."""

    job_id: str
    status: JobStatus
    message: str | None = None
    accepted_at: datetime | None = None
    estimated_completion: datetime | None = None

    model_config = dict(extra="forbid")
