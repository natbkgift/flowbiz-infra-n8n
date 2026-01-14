# Codex Pre-flight Checklist

## Purpose
This checklist ensures all changes align with FlowBiz template standards before merging.

## ⚠️ VPS Deployment Compliance (MANDATORY)

Before ANY deployment to shared FlowBiz VPS:

### Required Reading
- [ ] Read [docs/ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md) completely
- [ ] Read [docs/AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md) completely
- [ ] Read [docs/AGENT_BEHAVIOR_LOCK.md](AGENT_BEHAVIOR_LOCK.md) completely

### VPS Architecture Compliance
- [ ] Services bind to `127.0.0.1` (localhost) ONLY
- [ ] NO nginx in docker-compose.yml
- [ ] NO nginx in docker-compose.prod.yml
- [ ] NO reverse proxy containers (traefik, caddy, ingress, etc.)
- [ ] Port assignment is documented
- [ ] APP_HOST is set to `127.0.0.1` (NOT `0.0.0.0`)
- [ ] docker-compose ports use `127.0.0.1:PORT:PORT` format

### Health Endpoints
- [ ] GET /healthz works on http://127.0.0.1:PORT/healthz
- [ ] GET /v1/meta works on http://127.0.0.1:PORT/v1/meta
- [ ] Both return correct JSON structure
- [ ] Both return 200 status code

---

## Pre-Commit Checklist

### Code Quality
- [ ] Code follows existing style conventions
- [ ] No unused imports or variables
- [ ] No hardcoded credentials or secrets
- [ ] Error handling is appropriate
- [ ] Logging is consistent with existing patterns

### Testing
- [ ] All new code has corresponding tests
- [ ] Tests are deterministic (no random data, no network calls)
- [ ] `pytest -q` passes locally
- [ ] No tests were removed without justification

### Linting
- [ ] `ruff check .` passes without errors
- [ ] Code is formatted consistently
- [ ] Import order follows convention (stdlib, third-party, local)

### Documentation
- [ ] README.md updated if public interface changes
- [ ] Inline comments added for complex logic
- [ ] Docstrings present for public functions
- [ ] Environment variables documented in .env.example

## API Contract Verification

### Endpoints
- [ ] `/healthz` returns `{"status": "ok", "service": "...", "version": "..."}`
- [ ] `/v1/meta` returns `{"service": "...", "environment": "...", "version": "...", "build_sha": "..."}`
- [ ] No new endpoints added outside approved scope

### Response Format
- [ ] All responses are valid JSON
- [ ] Status codes are appropriate (200, 404, 500)
- [ ] Error responses follow schema

## Environment Conventions

### Variable Naming
- [ ] Runtime config uses `APP_*` prefix
- [ ] Metadata uses `FLOWBIZ_*` prefix
- [ ] No other prefixes introduced

### Configuration
- [ ] All new variables in `.env.example`
- [ ] Defaults provided in code
- [ ] Sensitive values not committed

## Docker & Infrastructure

### Docker
- [ ] `docker compose up` starts successfully
- [ ] Services bind to localhost (127.0.0.1) only
- [ ] Services can communicate internally
- [ ] Logs are visible with `docker compose logs`
- [ ] NO nginx service in docker-compose files

### Ports
- [ ] API runs on internal port 8000 (or assigned port)
- [ ] Port binds to 127.0.0.1 (localhost) only
- [ ] NO public binding (0.0.0.0)
- [ ] NO port conflicts
- [ ] Port documented in PROJECT_CONTRACT.md

### Security
- [ ] Service binds to localhost (127.0.0.1) only
- [ ] Security headers managed by system nginx (not in docker-compose)
- [ ] No security vulnerabilities introduced
- [ ] SSL/TLS managed by infrastructure (not in project)

## Scope Compliance

### ✅ In Scope
- [ ] Changes are template infrastructure
- [ ] No business-specific logic added
- [ ] Follows FlowBiz conventions

### ❌ Out of Scope (Must NOT be present)
- [ ] No authentication/authorization code
- [ ] No database models or migrations
- [ ] No billing or payment logic
- [ ] No user management
- [ ] No async workers or queues
- [ ] No cron jobs or scheduled tasks
- [ ] No UI/frontend code

## CI/CD

### Workflows
- [ ] `.github/workflows/ci.yml` runs successfully
- [ ] `.github/workflows/guardrails.yml` reports no violations
- [ ] `.github/workflows/pr-labels.yml` suggests correct labels

### PR Template
- [ ] Summary section completed
- [ ] Testing section completed
- [ ] Appropriate persona labels applied

## Documentation

### Core Docs
- [ ] `docs/ADR_SYSTEM_NGINX.md` referenced (for VPS projects)
- [ ] `docs/AGENT_NEW_PROJECT_CHECKLIST.md` referenced (for VPS projects)
- [ ] `docs/AGENT_BEHAVIOR_LOCK.md` referenced (for VPS projects)
- [ ] `docs/PROJECT_CONTRACT.md` reflects current API
- [ ] `docs/DEPLOYMENT.md` includes VPS deployment steps
- [ ] `docs/GUARDRAILS.md` updated with new rules (if any)
- [ ] This file updated with new checks (if any)

### README
- [ ] Installation instructions current
- [ ] Usage examples work
- [ ] Links are valid

## Final Verification

### Local Testing
```bash
# Clean start
docker compose down -v
docker compose up --build

# Test endpoints (note: 127.0.0.1, not 0.0.0.0)
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/v1/meta

# Verify localhost binding
netstat -tlnp | grep 8000  # Should show 127.0.0.1:8000, NOT 0.0.0.0:8000

# Run checks
ruff check .
pytest -q
```

### Deployment Simulation
```bash
# Test production compose
docker compose -f docker-compose.yml -f docker-compose.prod.yml config

# Verify no errors in output
```

## Sign-off

### Developer
- [ ] All checklist items reviewed
- [ ] No scope creep
- [ ] Ready for review

### Reviewer
- [ ] Code reviewed
- [ ] Tests validated
- [ ] Documentation approved
- [ ] Scope compliance verified

## Notes
- This checklist is a guide, not a blocker
- Use judgment for edge cases
- Document any deviations in PR description
- Update this checklist as standards evolve
