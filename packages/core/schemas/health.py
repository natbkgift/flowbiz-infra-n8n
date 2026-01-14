from packages.core.schemas.base import BaseResponse


class HealthResponse(BaseResponse):
    """Health check response model."""

    status: str
    service: str
    version: str


class MetaResponse(BaseResponse):
    """Service metadata response model."""

    service: str
    environment: str
    version: str
    build_sha: str
