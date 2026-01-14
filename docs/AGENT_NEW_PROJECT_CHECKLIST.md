# Agent New Project Checklist

## Purpose
This checklist ensures EVERY new client project is VPS-deployment-ready and complies with flowbiz-ai-core rules.

## CRITICAL: Pre-Deployment Gate
**IF ANY ITEM BELOW IS "NO" → DEPLOYMENT IS FORBIDDEN**

You MUST read and verify ALL items before proceeding with ANY deployment-related changes.

---

## Phase 1: Documentation Review

### Mandatory Reading (MUST be completed FIRST)
- [ ] I have read `docs/ADR_SYSTEM_NGINX.md` completely
- [ ] I have read `docs/AGENT_BEHAVIOR_LOCK.md` completely
- [ ] I have read `docs/AGENT_NEW_PROJECT_CHECKLIST.md` (this file) completely
- [ ] I understand the shared VPS architecture
- [ ] I understand why nginx is NOT in my docker-compose

### Understanding Check
- [ ] I can explain why services bind to 127.0.0.1 (localhost)
- [ ] I can explain the deployment flow (local → VPS → nginx → public)
- [ ] I know where system nginx configs live (/etc/nginx/sites-available/)
- [ ] I know who manages nginx (infrastructure team, NOT me)

---

## Phase 2: Project Configuration

### Port Assignment
- [ ] I have requested a unique port from infrastructure team
- [ ] Port is documented in PROJECT_CONTRACT.md
- [ ] Port is NOT already used by another project
- [ ] Port is in the valid range (typically 8000-8999)

### Service Binding
- [ ] APP_HOST is set to `127.0.0.1` (NOT `0.0.0.0`)
- [ ] APP_PORT matches assigned port
- [ ] No services expose public ports directly
- [ ] docker-compose.yml ports section maps correctly (e.g., "127.0.0.1:8001:8001")

### Health Endpoints
- [ ] GET /healthz endpoint exists
- [ ] GET /healthz returns JSON with status, service, version
- [ ] GET /v1/meta endpoint exists
- [ ] GET /v1/meta returns JSON with service, environment, version, build_sha
- [ ] Both endpoints return 200 OK when healthy

---

## Phase 3: Docker Configuration

### Docker Compose Structure
- [ ] docker-compose.yml exists for development
- [ ] docker-compose.prod.yml exists for production overrides
- [ ] NO nginx service in docker-compose.yml
- [ ] NO nginx service in docker-compose.prod.yml
- [ ] NO traefik, caddy, ingress, or other reverse proxy services

### Service Configuration
- [ ] Service binds to localhost (APP_HOST=127.0.0.1)
- [ ] Service uses assigned port (APP_PORT=XXXX)
- [ ] Port mapping is localhost-to-localhost (e.g., "127.0.0.1:8001:8001")
- [ ] Environment variables follow conventions (APP_*, FLOWBIZ_*)
- [ ] Restart policy is set (restart: unless-stopped or always)

### Container Health
- [ ] Dockerfile uses non-root user
- [ ] Health check is defined (optional but recommended)
- [ ] No secrets in Dockerfile or docker-compose
- [ ] Minimal base image is used

---

## Phase 4: Documentation

### Required Files
- [ ] docs/PROJECT_CONTRACT.md exists and is complete
- [ ] docs/DEPLOYMENT.md exists and reflects VPS architecture
- [ ] docs/GUARDRAILS.md exists
- [ ] docs/CODEX_PREFLIGHT.md exists
- [ ] README.md includes deployment warnings
- [ ] .env.example has all required variables

### PROJECT_CONTRACT.md Content
- [ ] Assigned port is documented
- [ ] Health endpoints are documented
- [ ] Environment variables are listed
- [ ] API contract is clear
- [ ] Localhost binding is specified

### DEPLOYMENT.md Content
- [ ] References ADR_SYSTEM_NGINX.md
- [ ] Explains localhost verification step
- [ ] States nginx is configured externally
- [ ] NO instructions for nginx editing
- [ ] NO instructions for nginx restart

---

## Phase 5: Local Verification

### Development Testing
- [ ] `docker compose up` starts successfully
- [ ] Service is accessible on http://127.0.0.1:8000/healthz (replace 8000 with your assigned port)
- [ ] Service is accessible on http://127.0.0.1:8000/v1/meta (replace 8000 with your assigned port)
- [ ] No errors in docker logs
- [ ] Service restarts automatically on code changes (dev mode)

### Health Endpoint Testing
```bash
# Replace 8000 with your assigned port if different
curl http://127.0.0.1:8000/healthz
# Expected: {"status":"ok","service":"...","version":"..."}

curl http://127.0.0.1:8000/v1/meta
# Expected: {"service":"...","environment":"...","version":"...","build_sha":"..."}
```

- [ ] /healthz returns correct JSON structure
- [ ] /healthz returns 200 status code
- [ ] /v1/meta returns correct JSON structure
- [ ] /v1/meta returns 200 status code

### Production Build Testing
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```
- [ ] Production build completes successfully
- [ ] Service starts in production mode
- [ ] Health endpoints work in production build
- [ ] No development volumes are mounted

---

## Phase 6: VPS Deployment Readiness

### Pre-Deployment Verification
- [ ] All previous checklist items are YES
- [ ] Code is committed to repository
- [ ] CI/CD passes (if configured)
- [ ] No hardcoded secrets or credentials
- [ ] .env file is NOT committed (only .env.example)

### Infrastructure Coordination
- [ ] Infrastructure team is aware of deployment
- [ ] Domain name is decided and communicated
- [ ] DNS will point to VPS IP
- [ ] SSL certificate plan is clear (Let's Encrypt)
- [ ] Port assignment is confirmed and documented

### Deployment Plan Understanding
- [ ] I will deploy service first (localhost only)
- [ ] I will verify local health endpoints
- [ ] I will request nginx configuration from infra team
- [ ] I will NOT touch nginx configs myself
- [ ] Public HTTPS verification is the LAST step

---

## Phase 7: Post-Deployment Verification

### After Service Deployment
```bash
# On VPS, as your user (replace 8000 with your assigned port)
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/v1/meta
```
- [ ] Service responds on localhost
- [ ] Health endpoints return correct responses
- [ ] Docker container is running
- [ ] Service logs show no errors

### After Nginx Configuration (by Infrastructure)
```bash
# After infra team configures nginx
curl https://domain.com/healthz
curl https://domain.com/v1/meta
```
- [ ] Service responds via HTTPS
- [ ] SSL certificate is valid
- [ ] All endpoints work through nginx
- [ ] Security headers are present

---

## Phase 8: Documentation & Handoff

### Final Documentation
- [ ] Deployed port documented in PROJECT_CONTRACT.md
- [ ] Domain documented in PROJECT_CONTRACT.md
- [ ] Health check URLs documented
- [ ] Deployment date recorded
- [ ] Any deployment notes added

### Knowledge Transfer
- [ ] Team knows how to access logs (`docker compose logs`)
- [ ] Team knows how to restart service (`docker compose restart`)
- [ ] Team knows NOT to touch nginx
- [ ] Team knows to escalate nginx issues to infra

---

## Red Flags - STOP Immediately If:

### 🚨 Configuration Red Flags
- ❌ APP_HOST is set to `0.0.0.0`
- ❌ Port is exposed publicly (not bound to localhost)
- ❌ Nginx is in docker-compose.yml
- ❌ Port conflicts with existing service
- ❌ No health endpoints exist

### 🚨 Documentation Red Flags
- ❌ Mandatory ADRs not read
- ❌ Port not assigned or documented
- ❌ DEPLOYMENT.md says to edit nginx
- ❌ Instructions mention nginx restart

### 🚨 Deployment Red Flags
- ❌ Attempting to configure nginx yourself
- ❌ Attempting to restart system nginx
- ❌ Assuming port availability
- ❌ Deploying without local verification
- ❌ Making assumptions about VPS layout

---

## Emergency Procedures

### If You Find a Red Flag
1. **STOP immediately**
2. Do NOT proceed with deployment
3. Fix the issue
4. Re-verify ALL checklist items
5. Only proceed when ALL items are YES

### If You're Unsure
1. **STOP and document your question**
2. Create a documentation-only proposal
3. Escalate to infrastructure team
4. Do NOT make assumptions
5. Wait for clarification before proceeding

### If Something Breaks
- Service won't start: Check logs, verify env variables, check port conflicts
- Can't access locally: Verify APP_HOST=127.0.0.1 and port
- Can't access publicly: Contact infra team (nginx issue)
- SSL certificate issues: Contact infra team
- Port conflicts: Request different port, update docs

---

## Sign-Off

Before ANY deployment code or configuration changes:

**Developer Sign-Off:**
- [ ] I have read and understood all mandatory documentation
- [ ] ALL checklist items are verified as YES
- [ ] I understand my deployment is localhost-only initially
- [ ] I understand nginx configuration is NOT my responsibility
- [ ] I will coordinate with infrastructure team for public access

**Date:** _____________  
**Developer Name:** _____________  
**Project Name:** _____________  
**Assigned Port:** _____________  
**Target Domain:** _____________

---

## Maintenance

This checklist should be:
- Updated when VPS architecture changes
- Reviewed before each new project deployment
- Referenced in all deployment documentation
- Enforced by CI/CD where possible

## Questions?
- Unclear about any item? Ask before proceeding
- Found a gap in the checklist? Submit an issue
- Documentation conflicts? ADRs and this checklist win
