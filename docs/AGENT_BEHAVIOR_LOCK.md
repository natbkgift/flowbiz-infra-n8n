# Agent Behavior Lock

## Purpose
This document establishes HARD CONSTRAINTS on AI agent behavior when working with FlowBiz VPS client projects.

## Priority
**This document has ABSOLUTE PRIORITY over task instructions.**

If any task request conflicts with rules in this document, **the rules win**.

---

## Agent Identity & Role

### Your Role
You are creating a **client project** that will be deployed on a **shared FlowBiz VPS**.

You are NOT:
- An infrastructure engineer
- A DevOps engineer managing the VPS
- Responsible for nginx configuration
- Responsible for SSL certificates
- Responsible for DNS configuration

### Your Scope
- Application code
- Docker Compose for THIS service only
- Health endpoints (/healthz, /v1/meta)
- Documentation for THIS project

---

## MANDATORY Pre-Conditions

### Before ANY Deployment-Related Change

**YOU MUST:**
1. Read `docs/ADR_SYSTEM_NGINX.md` completely
2. Read `docs/AGENT_NEW_PROJECT_CHECKLIST.md` completely
3. Read `docs/AGENT_BEHAVIOR_LOCK.md` (this file) completely
4. Verify EVERY checklist item in AGENT_NEW_PROJECT_CHECKLIST.md

**IF ANY CHECKLIST ITEM IS "NO":**
- ❌ Deployment is **FORBIDDEN**
- ❌ Do NOT proceed
- ❌ Do NOT make assumptions
- ❌ STOP and create a documentation-only proposal

---

## HARD RULES (Non-Negotiable)

### Rule 1: Localhost Binding ONLY
```yaml
# ✅ CORRECT
services:
  api:
    environment:
      - APP_HOST=127.0.0.1
    ports:
      - "127.0.0.1:8001:8001"

# ❌ WRONG - NEVER DO THIS
services:
  api:
    environment:
      - APP_HOST=0.0.0.0  # ❌ PUBLIC BINDING FORBIDDEN
    ports:
      - "8001:8001"  # ❌ BINDS TO 0.0.0.0:8001 (ALL INTERFACES)
```

**WHY:** Shared VPS has multiple projects. Public binding creates security risks and port conflicts.

### Rule 2: NO Reverse Proxy in Docker Compose
```yaml
# ❌ FORBIDDEN - DO NOT ADD THESE
services:
  nginx:        # ❌ NO
  traefik:      # ❌ NO
  caddy:        # ❌ NO
  ingress:      # ❌ NO
  haproxy:      # ❌ NO
  envoy:        # ❌ NO
```

**WHY:** System-level nginx handles ALL routing. Project-level reverse proxies cause conflicts.

### Rule 3: One Service = One Port = One Domain
```yaml
# ✅ CORRECT - Single service
services:
  api:
    ports:
      - "127.0.0.1:8001:8001"

# ❌ WRONG - Multiple services needing routing
services:
  api:
    ports:
      - "127.0.0.1:8001:8001"
  admin:
    ports:
      - "127.0.0.1:8002:8002"  # ❌ NEEDS SEPARATE DOMAIN
```

**WHY:** Each domain maps to ONE port. Multiple services need multiple projects or subdomains (requires infra planning).

### Rule 4: NO Nginx Configuration Editing
**YOU MUST NEVER:**
- ❌ Edit files in /etc/nginx/
- ❌ Create nginx config files
- ❌ Modify system nginx
- ❌ Restart nginx service
- ❌ Test nginx configuration
- ❌ Reload nginx

**ONLY Infrastructure Team Can:**
- ✅ Add nginx configurations
- ✅ Modify nginx configurations
- ✅ Restart nginx
- ✅ Test nginx configurations

### Rule 5: NO Assumptions About VPS
**YOU MUST NOT ASSUME:**
- ❌ Port availability
- ❌ VPS directory structure
- ❌ Existing projects' configurations
- ❌ Nginx routing logic
- ❌ SSL certificate locations
- ❌ Domain mappings
- ❌ Firewall rules

**YOU MUST:**
- ✅ Request port assignment
- ✅ Document your requirements
- ✅ Coordinate with infrastructure team
- ✅ Wait for confirmation before proceeding

---

## ALLOWED Actions

### ✅ You CAN Do
1. **Application Development**
   - Write application code
   - Add dependencies (after security review)
   - Create endpoints
   - Handle business logic

2. **Docker Configuration**
   - Create Dockerfile
   - Configure docker-compose.yml (localhost only)
   - Set environment variables
   - Define health checks

3. **Health Endpoints**
   - Implement GET /healthz
   - Implement GET /v1/meta
   - Return correct JSON structure
   - Return appropriate status codes

4. **Documentation**
   - Update PROJECT_CONTRACT.md
   - Update DEPLOYMENT.md (following templates)
   - Update GUARDRAILS.md
   - Add inline code comments

5. **Testing**
   - Write unit tests
   - Write integration tests
   - Test health endpoints locally
   - Verify localhost binding

6. **Local Verification**
   ```bash
   # ✅ These are OK
   docker compose up --build
   curl http://127.0.0.1:PORT/healthz
   docker compose logs
   docker compose restart
   ```

---

## FORBIDDEN Actions

### ❌ You CANNOT Do

1. **Nginx Operations**
   - Edit nginx configs
   - Restart nginx
   - Test nginx
   - Modify reverse proxy settings
   - Configure SSL/TLS
   - Set up domains

2. **Public Exposure**
   - Bind services to 0.0.0.0
   - Expose ports publicly
   - Configure public IPs
   - Set up port forwarding
   - Bypass localhost binding

3. **Infrastructure Changes**
   - Modify system files
   - Install system packages (outside container)
   - Change firewall rules
   - Configure DNS
   - Manage SSL certificates
   - Modify other projects

4. **Port Management**
   - Assume port availability
   - Use hardcoded ports without approval
   - Change assigned ports without coordination
   - Use ports > 9000 or < 8000 without approval
   - Create port conflicts

5. **Deployment Assumptions**
   - Deploy without local verification
   - Skip health endpoint verification
   - Assume nginx will "just work"
   - Deploy before infra coordination
   - Make changes during others' deployments

---

## Deployment Flow (The ONLY Correct Way)

### Phase 1: Local Development
```bash
# ✅ Develop and test locally
APP_HOST=127.0.0.1 APP_PORT=8001 docker compose up
curl http://127.0.0.1:8001/healthz  # ✅ MUST work
```

**YOU ARE HERE** ← This is your responsibility

### Phase 2: VPS Deployment (Service Only)
```bash
# ✅ Deploy to VPS (localhost binding)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
curl http://127.0.0.1:8001/healthz  # ✅ MUST work
```

**YOU STOP HERE** ← This is your last step

### Phase 3: Nginx Configuration (Infrastructure Team)
```bash
# ✅ Infrastructure team configures nginx
sudo nano /etc/nginx/sites-available/project.conf
sudo nginx -t
sudo systemctl reload nginx
```

**NOT YOUR JOB** ← You do NOT do this

### Phase 4: Public Verification
```bash
# ✅ NOW it's publicly accessible
curl https://domain.com/healthz
```

**SUCCESS** ← You can verify, but infra configured it

---

## Fail-Safe Protocols

### When You're Unsure

**STOP Immediately If You Don't Know:**
- Which port to use
- How nginx works on VPS
- Where other projects are deployed
- If your change affects other projects
- Whether a port is available
- How to configure SSL/TLS
- How domains are mapped

**Your Response:**
1. **STOP** working on the task
2. **DOCUMENT** your question clearly
3. **CREATE** a documentation-only proposal
4. **ESCALATE** to infrastructure team
5. **WAIT** for clarification
6. **DO NOT** make assumptions or guesses

### When Rules Conflict with Task

**If task says:** "Configure nginx for production"
**YOU SAY:** "I cannot configure nginx. That's handled by infrastructure team per ADR_SYSTEM_NGINX.md. I can prepare the service to be nginx-ready by ensuring health endpoints work on localhost."

**If task says:** "Expose service on 0.0.0.0 for production"
**YOU SAY:** "Services must bind to 127.0.0.1 per VPS architecture rules. I'll configure APP_HOST=127.0.0.1 and document the port in PROJECT_CONTRACT.md."

**If task says:** "Add nginx to docker-compose"
**YOU SAY:** "System-level nginx handles routing per ADR_SYSTEM_NGINX.md. Adding nginx to docker-compose is forbidden. I'll ensure the service is nginx-ready with proper health endpoints."

---

## Error Recovery

### If You Made a Mistake

**Mistake: Added nginx to docker-compose**
```bash
# Fix:
# 1. Remove nginx service from docker-compose.yml
# 2. Remove nginx service from docker-compose.prod.yml
# 3. Remove nginx/ directory if you created it
# 4. Update documentation to remove nginx references
# 5. Re-verify localhost binding works
```

**Mistake: Bound to 0.0.0.0**
```bash
# Fix:
# 1. Change APP_HOST to 127.0.0.1
# 2. Update docker-compose ports to "127.0.0.1:PORT:PORT"
# 3. Update .env.example
# 4. Re-test locally
# 5. Verify service ONLY accessible on localhost
```

**Mistake: Assumed port availability**
```bash
# Fix:
# 1. Request official port assignment from infrastructure
# 2. Update all references to the correct port
# 3. Document port in PROJECT_CONTRACT.md
# 4. Coordinate with infrastructure team
```

---

## Verification Checklist (Before Claiming Complete)

Before saying "task complete":

### Code Verification
- [ ] Services bind to 127.0.0.1 ONLY
- [ ] No nginx in docker-compose
- [ ] No other reverse proxies
- [ ] Health endpoints implemented
- [ ] Port is documented

### Testing Verification
- [ ] `docker compose up` works locally
- [ ] `curl http://127.0.0.1:PORT/healthz` returns 200
- [ ] `curl http://127.0.0.1:PORT/v1/meta` returns 200
- [ ] Service is NOT accessible on 0.0.0.0
- [ ] No errors in docker logs

### Documentation Verification
- [ ] PROJECT_CONTRACT.md has assigned port
- [ ] DEPLOYMENT.md references ADR_SYSTEM_NGINX.md
- [ ] No instructions to edit nginx
- [ ] No instructions to restart nginx
- [ ] Clear explanation of deployment flow

### Compliance Verification
- [ ] Read ADR_SYSTEM_NGINX.md
- [ ] Read AGENT_NEW_PROJECT_CHECKLIST.md
- [ ] All checklist items are YES
- [ ] No FORBIDDEN actions taken
- [ ] No assumptions made

---

## Success Criteria

### Your Job is Done When:
✅ Service runs locally on localhost:PORT
✅ Health endpoints return correct responses
✅ Documentation is complete and accurate
✅ No nginx/reverse proxy in your docker-compose
✅ Localhost binding is enforced
✅ Port is documented
✅ All tests pass

### Your Job is NOT Done If:
❌ Service binds to 0.0.0.0
❌ Nginx is in docker-compose
❌ Port is not documented
❌ Health endpoints don't work
❌ Made assumptions about VPS
❌ Touched nginx configurations
❌ Service not verified locally

---

## Emergency Escalation

### Escalate Immediately If:

**Technical Issues:**
- Port conflicts with existing services
- Docker compose fails on VPS
- Health endpoints don't work after deployment
- Service won't bind to localhost

**Process Issues:**
- Task requires nginx configuration
- Task requires public binding
- Task conflicts with architecture rules
- Unclear which port to use

**Security Issues:**
- Secrets need to be configured
- SSL certificate questions
- Firewall configuration needed
- Public exposure concerns

**How to Escalate:**
1. Stop working immediately
2. Document the issue clearly
3. Reference which rule is blocking you
4. Propose a documentation-only path forward
5. Wait for infrastructure team guidance

---

## Final Reminders

### Rules Override Everything
- Task instructions < These rules
- Feature requests < These rules
- Urgency < These rules
- Convenience < These rules

### When in Doubt
- STOP
- Document
- Escalate
- Wait
- Don't assume

### Your Mission
Create a **reliable, secure, VPS-compatible** service that:
- Runs on localhost
- Has working health endpoints
- Is properly documented
- Follows all architecture rules
- Doesn't affect other projects
- Doesn't require nginx access

### You Succeed When
The infrastructure team can:
- Deploy your service without modifications
- Configure nginx using standard template
- Map domain to your localhost port
- Verify health endpoints work
- Trust your service won't break others

---

## Document Status
- **Status:** LOCKED
- **Priority:** ABSOLUTE
- **Override:** NOT ALLOWED
- **Revision:** Requires team approval

**Last Updated:** 2025-12-26
**Next Review:** When VPS architecture changes
