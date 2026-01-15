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
from packages.core.schemas.job import (
    JobCancelRequest,
    JobCancelResponse,
    JobRequest,
    JobResponse,
    JobStatus,
)

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


def _cancel_log_extra(job_id: str, payload: JobCancelRequest, status: JobStatus) -> dict[str, object]:
    """Structured logging for cancel operations."""

    return {
        "job_id": job_id,
        "client_id": payload.client_id,
        "workflow_key": payload.workflow_key,
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


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=JobCancelResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_job(job_id: str, request: JobCancelRequest) -> JobCancelResponse:
    """Deactivate the targeted workflow via n8n and mark the job cancelled."""

    if not workflow_exists(request.workflow_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown workflow_key",
        )

    if not settings.n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kill-switch unavailable: N8N_API_KEY not configured",
        )

    deactivated = await deactivate_workflow(request.workflow_key)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found in n8n",
        )

    response = JobCancelResponse(
        job_id=job_id,
        status=JobStatus.CANCELLED,
        message="cancelled",
        workflow_deactivated=True,
    )

    logger.info("job cancelled", extra=_cancel_log_extra(job_id, request, response.status))

    return response


async def deactivate_workflow(workflow_key: str) -> bool:
    """Deactivate the matching workflow in n8n; returns True if deactivated."""

    base_url = settings.n8n_api_base_url.rstrip("/")
    headers = {"X-N8N-API-KEY": settings.n8n_api_key or ""}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            list_response = await client.get(f"{base_url}/workflows", headers=headers)
            list_response.raise_for_status()

            payload = list_response.json()
            workflows = payload.get("data") if isinstance(payload, dict) else payload
            if not isinstance(workflows, list):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Unexpected n8n response shape",
                )

            workflow_id = _find_workflow_id(workflow_key, workflows)
            if not workflow_id:
                return False

            patch_response = await client.patch(
                f"{base_url}/workflows/{workflow_id}",
                headers=headers,
                json={"active": False},
            )
            patch_response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(
            "n8n kill-switch call failed",
            extra={
                "job_id": None,
                "client_id": None,
                "workflow_key": workflow_key,
                "status": JobStatus.CANCELLED,
            },
            exc_info=exc,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to deactivate workflow via n8n",
        ) from exc

    return True


def _find_workflow_id(workflow_key: str, workflows: list[dict[str, object]]) -> str | None:
    """Best-effort lookup to map registry key to n8n workflow id."""

    for workflow in workflows:
        if not isinstance(workflow, dict):
            continue

        name = workflow.get("name") or workflow.get("displayName")
        identifier = workflow.get("id")

        if name == workflow_key or str(identifier) == workflow_key:
            return str(identifier)

    return None


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
