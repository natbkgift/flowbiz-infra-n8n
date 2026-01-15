from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.registry import workflow_exists
from packages.core.schemas.job import JobRequest, JobResponse, JobStatus

router = APIRouter(prefix="/v1")
logger = get_logger(__name__)
_rate_limit_lock = threading.Lock()
_rate_limit_hits: dict[str, deque[float]] = defaultdict(deque)


def _job_log_extra(request: JobRequest, status: JobStatus) -> dict[str, object]:
    """Structured logging payload shared by handlers."""

    return {
        "job_id": request.job_id,
        "client_id": request.client_id,
        "workflow_key": request.workflow_key,
        "status": status,
    }


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks) -> JobResponse:
    """Accept a job request, validate workflow, and dispatch asynchronously."""

    if request.timeout_seconds > settings.jobs_max_timeout_seconds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="timeout_seconds exceeds maximum allowed",
        )

    if _rate_limit_exceeded(request.client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    if not workflow_exists(request.workflow_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown workflow_key",
        )

    accepted_at = datetime.now(timezone.utc)
    response = JobResponse(
        job_id=request.job_id,
        status=JobStatus.PENDING,
        message="accepted",
        accepted_at=accepted_at,
    )

    background_tasks.add_task(dispatch_to_n8n, request)

    logger.info("job accepted", extra=_job_log_extra(request, response.status))

    return response


async def dispatch_to_n8n(request: JobRequest) -> None:
    """Fire-and-forget call to n8n webhook; failures are logged."""

    webhook_url = f"{settings.n8n_webhook_base_url.rstrip('/')}/{request.workflow_key}"
    payload = request.model_dump(mode="json")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("n8n dispatch failed", extra=_job_log_extra(request, JobStatus.PENDING))
        logger.debug("dispatch exception", exc_info=exc)


def _rate_limit_exceeded(client_id: str) -> bool:
    """Return True if the client exceeds the per-minute limit."""

    limit = settings.jobs_rate_limit_per_minute
    if limit <= 0:
        return False

    now = time.monotonic()
    window_start = now - 60.0

    with _rate_limit_lock:
        hits = _rate_limit_hits[client_id]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= limit:
            return True
        hits.append(now)

    return False
