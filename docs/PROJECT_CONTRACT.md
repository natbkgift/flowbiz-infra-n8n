# Project Contract

## Overview
This document defines the core contract for FlowBiz template-based client services.

## API Endpoints

### GET /healthz
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "service": "service-name",
  "version": "0.1.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

### GET /v1/meta
Service metadata endpoint.

**Response:**
```json
{
  "service": "service-name",
  "environment": "dev|prod",
  "version": "0.1.0",
  "build_sha": "abc123"
}
```

**Status Codes:**
- `200 OK`: Metadata retrieved successfully

## Environment Variables

### Runtime Configuration (APP_*)
- `APP_ENV`: Environment (dev|prod)
- `APP_HOST`: Bind host (default: 127.0.0.1) ⚠️ MUST be localhost for VPS deployment
- `APP_PORT`: Bind port (default: 8000)
- `APP_LOG_LEVEL`: Logging level (default: info)

### Metadata (FLOWBIZ_*)
- `FLOWBIZ_SERVICE_NAME`: Service identifier
- `FLOWBIZ_VERSION`: Semantic version
- `FLOWBIZ_BUILD_SHA`: Git commit SHA

## Docker

### Ports
- Internal: 8000 (FastAPI/Uvicorn, bound to 127.0.0.1)
- External: Managed by system-level nginx (see ADR_SYSTEM_NGINX.md)

⚠️ **IMPORTANT:** Services bind to localhost (127.0.0.1) only. Public access is handled by system-level nginx configured by infrastructure team.

### Volumes
- Development: Hot-reload enabled
- Production: No volumes mounted

## Testing Requirements

All tests must be:
- **Deterministic**: No flaky tests
- **Isolated**: No network calls
- **Fast**: Complete in seconds

### Commands
```bash
ruff check .       # Linting
pytest -q          # Tests
```

## Security Headers (Nginx)

Production deployments include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security` (when SSL configured)

## Scope Boundaries

### ✅ In Scope
- Standard health/meta endpoints
- Docker containerization
- Nginx reverse proxy
- Environment configuration
- Testing infrastructure

### ❌ Out of Scope
- Business logic endpoints
- Authentication/Authorization
- Database integration
- Queue/Worker systems
- UI/Frontend code
- FlowBiz Core runtime

## Versioning
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes
