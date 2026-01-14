# FlowBiz Template Service

> ⚠️ **CRITICAL: MANDATORY PRE-DEPLOYMENT READING**  
> Before deploying this project to a shared FlowBiz VPS, you MUST read:  
> - [docs/ADR_SYSTEM_NGINX.md](docs/ADR_SYSTEM_NGINX.md) - System architecture (WHY nginx is external)
> - [docs/AGENT_NEW_PROJECT_CHECKLIST.md](docs/AGENT_NEW_PROJECT_CHECKLIST.md) - Complete deployment checklist
> - [docs/AGENT_BEHAVIOR_LOCK.md](docs/AGENT_BEHAVIOR_LOCK.md) - Strict deployment rules
>   
> **IF ANY CHECKLIST ITEM IS "NO" → DEPLOYMENT IS FORBIDDEN**  
> Deploying without reading these documents violates project rules.

**Related:** See [natbkgift/flowbiz-ai-core](https://github.com/natbkgift/flowbiz-ai-core) for VPS infrastructure documentation.

[![CI](https://github.com/natbkgift/flowbiz-template-service/actions/workflows/ci.yml/badge.svg)](https://github.com/natbkgift/flowbiz-template-service/actions/workflows/ci.yml)

Production-ready client service template for FlowBiz AI Core integration. This is a **template repository** designed for reuse across customer projects.

## 🎯 Purpose

This template provides:
- Standard API contracts (`/healthz`, `/v1/meta`)
- Docker containerization with Nginx reverse proxy
- Environment configuration conventions
- CI/CD with non-blocking guardrails
- Production deployment patterns

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Development

```bash
# Clone repository
git clone https://github.com/natbkgift/flowbiz-template-service.git
cd flowbiz-template-service

# Start services (binds to localhost:8000)
docker compose up --build

# Verify (note: localhost, not 0.0.0.0)
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/v1/meta
```

### Local Python Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Run application
python apps/api/main.py

# Run tests
pytest -q

# Run linting
ruff check .
```

## 📋 API Endpoints

### `GET /healthz`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "service": "flowbiz-template-service",
  "version": "0.1.0"
}
```

### `GET /v1/meta`
Service metadata endpoint.

**Response:**
```json
{
  "service": "flowbiz-template-service",
  "environment": "dev",
  "version": "0.1.0",
  "build_sha": "abc123"
}
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

**Runtime (APP_*)**
- `APP_ENV`: Environment (`dev`|`prod`)
- `APP_HOST`: Bind host (default: `127.0.0.1`) ⚠️ MUST be localhost for VPS
- `APP_PORT`: Bind port (default: `8000`)
- `APP_LOG_LEVEL`: Log level (default: `info`)

**Metadata (FLOWBIZ_*)**
- `FLOWBIZ_SERVICE_NAME`: Service identifier
- `FLOWBIZ_VERSION`: Semantic version
- `FLOWBIZ_BUILD_SHA`: Git commit SHA

## 🐳 Docker

### Development
```bash
docker compose up --build
```

### Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Verify local access (service binds to localhost only)
curl http://127.0.0.1:8000/healthz
```

**⚠️ Important:** 
- Service binds to `127.0.0.1` (localhost) only
- NO nginx included in docker-compose (managed by system-level nginx)
- See [docs/ADR_SYSTEM_NGINX.md](docs/ADR_SYSTEM_NGINX.md) for architecture
- Public HTTPS access configured by infrastructure team

## 🧪 Testing

All tests are deterministic with no external dependencies.

```bash
# Run tests
pytest -q

# Run with coverage
pytest --cov=apps --cov=packages

# Run specific test
pytest tests/test_health.py -v
```

## 🔒 Security

### VPS Architecture
- Services bind to **localhost (127.0.0.1) only**
- System-level nginx handles public routing and SSL
- No nginx in docker-compose (see [ADR_SYSTEM_NGINX.md](docs/ADR_SYSTEM_NGINX.md))

### Security Headers (Managed by System Nginx)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security` (production with SSL)

### Best Practices
- No secrets in code or environment files
- Non-root container user
- Minimal base images
- Regular dependency updates

## 📚 Documentation

- **[ADR: System Nginx](docs/ADR_SYSTEM_NGINX.md)** - ⚠️ MANDATORY - VPS architecture overview
- **[New Project Checklist](docs/AGENT_NEW_PROJECT_CHECKLIST.md)** - ⚠️ MANDATORY - Pre-deployment verification
- **[Agent Behavior Lock](docs/AGENT_BEHAVIOR_LOCK.md)** - ⚠️ MANDATORY - Deployment rules and constraints
- [Project Contract](docs/PROJECT_CONTRACT.md) - API contracts and conventions
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment steps
- [Guardrails](docs/GUARDRAILS.md) - CI/CD philosophy and rules
- [Pre-flight Checklist](docs/CODEX_PREFLIGHT.md) - Pre-merge verification

## 🛡️ Guardrails

This project uses **non-blocking** CI guardrails:
- Linting with `ruff`
- Testing with `pytest`
- Scope validation
- PR template requirements

Violations surface as warnings, not failures. Human judgment is final.

## 📦 Project Structure

```
flowbiz-template-service/
├── .github/              # CI/CD workflows and templates
├── apps/
│   └── api/              # FastAPI application
│       ├── main.py
│       └── routes/       # API endpoints
├── packages/
│   └── core/             # Shared core modules
│       ├── config.py     # Environment configuration
│       ├── logging.py    # Logging setup
│       └── schemas/      # Pydantic models
├── nginx/                # Nginx reference templates (NOT used in docker-compose)
│   ├── templates/        # Config templates for infrastructure team
│   └── snippets/         # Reusable config snippets
├── docs/                 # Documentation
├── tests/                # Test suite
├── Dockerfile            # Container definition
├── docker-compose.yml    # Development compose
├── docker-compose.prod.yml # Production overrides
└── pyproject.toml        # Python project config
```

## 🚫 Scope Boundaries

### ✅ In Scope
- Standard health/meta endpoints
- Docker containerization (service only)
- Localhost binding (127.0.0.1)
- Environment configuration
- CI/CD infrastructure

### ❌ Out of Scope
- Nginx configuration (managed by system-level nginx)
- SSL/TLS certificates (managed by infrastructure)
- Public port exposure (services bind to localhost only)
- Business logic endpoints
- Authentication/Authorization
- Database integrations
- Queue/Worker systems
- UI/Frontend code
- FlowBiz Core runtime

**See [AGENT_BEHAVIOR_LOCK.md](docs/AGENT_BEHAVIOR_LOCK.md) for complete rules.**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following conventions
4. Run tests and linting
5. Submit PR with completed template
6. Apply appropriate persona labels

See [CODEX_PREFLIGHT.md](docs/CODEX_PREFLIGHT.md) for detailed checklist.

## 📝 License

This template is maintained by FlowBiz AI Core team.

## 🔗 Links

- [FlowBiz AI Core](https://github.com/natbkgift)
- [Documentation](docs/)
- [Issues](https://github.com/natbkgift/flowbiz-template-service/issues)