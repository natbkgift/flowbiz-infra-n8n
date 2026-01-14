# ADR: System-Level Nginx Architecture

## Status
**ACCEPTED** - This is the mandatory architecture for all FlowBiz VPS client projects.

## Context
Multiple client projects must coexist on a single shared FlowBiz VPS. Each project needs:
- Unique domain routing
- SSL/TLS termination
- Security headers
- Isolation from other projects
- Zero-downtime deployments

## Decision
We use a **single, system-level Nginx** instance managed outside individual project repositories.

### Architecture Overview
```
Internet (HTTPS)
    ↓
[System Nginx] (Port 80/443)
    ↓ Reverse Proxy
    ├─→ Project A (127.0.0.1:8001) → domain-a.com
    ├─→ Project B (127.0.0.1:8002) → domain-b.com
    └─→ Project C (127.0.0.1:8003) → domain-c.com
```

### Rules for Client Projects

#### ✅ REQUIRED
1. **Localhost Binding Only**
   - Services MUST bind to `127.0.0.1` (localhost)
   - NEVER bind to `0.0.0.0` (all interfaces)
   - Each project gets a unique port

2. **Health Endpoints**
   - `GET /healthz` - Service health check
   - `GET /v1/meta` - Service metadata

3. **Port Assignment**
   - Request port assignment from infrastructure team
   - Document assigned port in PROJECT_CONTRACT.md
   - One service = one port = one domain

4. **No Internal Nginx**
   - Do NOT include nginx in docker-compose.yml
   - Do NOT include ingress controllers
   - Do NOT include traefik, caddy, or other reverse proxies

#### ❌ FORBIDDEN
1. **Public Binding**
   - Never expose services on 0.0.0.0
   - Never bind to public IPs directly

2. **Port Conflicts**
   - Never assume port availability
   - Never hardcode ports without approval

3. **Nginx Configuration**
   - Never edit system nginx configs
   - Never restart system nginx
   - Never modify other projects' configs

4. **Assumptions**
   - Never assume VPS layout
   - Never assume routing logic
   - Never assume SSL configuration

### System Nginx Configuration (Reference Only)
Managed by infrastructure team at `/etc/nginx/sites-available/`:

```nginx
# Example: /etc/nginx/sites-available/project-name.conf
upstream project_name {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name domain.com;

    ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;

    location / {
        proxy_pass http://project_name;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

### Deployment Flow

#### Phase 1: Local Development
```bash
# Service runs on localhost
APP_HOST=127.0.0.1 APP_PORT=8001 docker compose up
curl http://127.0.0.1:8001/healthz
```

#### Phase 2: VPS Deployment
```bash
# Deploy service (binds to localhost:PORT)
docker compose up -d

# Verify local access
curl http://127.0.0.1:8001/healthz
```

#### Phase 3: Nginx Configuration (Infrastructure Team)
```bash
# Infrastructure team adds nginx config
sudo nano /etc/nginx/sites-available/project-name.conf
sudo ln -s /etc/nginx/sites-available/project-name.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Phase 4: DNS & SSL (Infrastructure Team)
```bash
# Point domain to VPS
# Configure Let's Encrypt
sudo certbot --nginx -d domain.com
```

#### Phase 5: Public Verification
```bash
# Now accessible via HTTPS
curl https://domain.com/healthz
```

## Consequences

### Positive
- **Centralized SSL Management**: One place for certificates
- **Project Isolation**: Projects cannot interfere with each other
- **Zero Downtime**: Nginx stays up during project restarts
- **Security**: Localhost binding prevents direct external access
- **Simplicity**: Projects focus on application logic only

### Negative
- **Infrastructure Dependency**: Requires coordination with infra team
- **Two-Step Deployment**: Service first, then nginx config
- **Port Management**: Requires port registry

### Neutral
- **Learning Curve**: Developers must understand the architecture
- **Documentation**: Clear docs required (this file)

## Compliance
Before ANY deployment:
1. Read this ADR
2. Read AGENT_NEW_PROJECT_CHECKLIST.md
3. Read AGENT_BEHAVIOR_LOCK.md
4. Verify ALL checklist items are YES
5. If ANY item is NO → Deployment is FORBIDDEN

## Emergency Contacts
- Infrastructure issues: Escalate to infra team
- Port conflicts: Check port registry, request new port
- Nginx debugging: Do NOT attempt fixes yourself
- SSL certificate issues: Contact infra team

## References
- AGENT_NEW_PROJECT_CHECKLIST.md - Pre-deployment verification
- AGENT_BEHAVIOR_LOCK.md - Agent behavior constraints
- PROJECT_CONTRACT.md - Service-specific configuration
- DEPLOYMENT.md - Step-by-step deployment guide

## Revision History
- 2025-12-26: Initial ADR for shared VPS architecture
