from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CallbackStatus(StrEnum):
    """Completion state reported by n8n."""

    SUCCESS = "success"
    FAILED = "failed"


class AuditEntry(BaseModel):
    """Per-node audit trace for a workflow execution."""

    timestamp: datetime
    action: str
    node_name: str
    details: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = Field(default=0, ge=0)

    model_config = dict(extra="forbid")


class JobCallback(BaseModel):
    """Callback payload posted by n8n."""

    job_id: str
    status: CallbackStatus
    outputs: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    audit: list[AuditEntry] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_id: str | None = None

    model_config = dict(extra="forbid")
