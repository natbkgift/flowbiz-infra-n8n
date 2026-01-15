from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class WorkflowMetadata(BaseModel):
    """Metadata for a workflow entry in the registry."""

    key: str
    name: str
    version: str
    description: str | None = None


class WorkflowRegistry(BaseModel):
    """Registry document definition."""

    workflows: list[WorkflowMetadata]


REGISTRY_PATH = Path(__file__).resolve().parents[2] / "workflows" / "registry.json"


def _load_registry() -> WorkflowRegistry:
    """Load the workflow registry from disk."""

    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Registry file not found at {REGISTRY_PATH}")

    raw = REGISTRY_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)
    return WorkflowRegistry(**data)


@lru_cache
def get_registry() -> WorkflowRegistry:
    """Cached registry accessor to avoid repeated disk reads."""

    return _load_registry()


def workflow_exists(workflow_key: str) -> bool:
    """Return True if workflow_key is present in the registry."""

    registry = get_registry()
    return any(entry.key == workflow_key for entry in registry.workflows)