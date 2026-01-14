# Deployment Guide

## ⚠️ CRITICAL: VPS Deployment Pre-Requisites

**BEFORE deploying to shared FlowBiz VPS, you MUST read:**
1. [docs/ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md) - System architecture
2. [docs/AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md) - Deployment checklist
3. [docs/AGENT_BEHAVIOR_LOCK.md](AGENT_BEHAVIOR_LOCK.md) - Deployment rules

**IF ANY CHECKLIST ITEM IS "NO" → DEPLOYMENT IS FORBIDDEN**

---

## Prerequisites
- Docker & Docker Compose
- Git
- (Production) VPS with public IP
- (Production) Domain name & SSL certificate

## Development Deployment

### 1. Clone Repository
```bash
git clone https://github.com/natbkgift/flowbiz-template-service.git
cd flowbiz-template-service
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Services
```bash
docker compose up --build
```

### 4. Verify
```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/v1/meta
```

**Note:** Service binds to localhost (127.0.0.1) only, as required by VPS architecture.

---

## Production Deployment on Shared VPS

### Architecture Overview
This service follows the **system-level nginx** architecture (see [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md)):
- Service binds to `127.0.0.1:PORT` (localhost only)
- System nginx handles public routing, SSL, and domain mapping
- Infrastructure team configures nginx (NOT you)

### Deployment Flow
1. **Deploy service** (localhost binding) → YOU do this
2. **Verify locally** → YOU do this
3. **Request nginx config** → Infrastructure team does this
4. **Verify public HTTPS** → After infrastructure completes

---

### 1. Server Setup
```bash
# SSH into your VPS
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 2. Deploy Application
```bash
git clone https://github.com/natbkgift/flowbiz-template-service.git
cd flowbiz-template-service

# Create production environment file
cp .env.example .env
nano .env
# Set:
# APP_ENV=prod
# FLOWBIZ_BUILD_SHA=$(git rev-parse HEAD)
```

### 3. Start Production Stack
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 4. Verify Local Access (CRITICAL)
```bash
# Service MUST respond on localhost
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/v1/meta
```

✅ **If these work, YOUR deployment is complete.**

### 5. Request Nginx Configuration (Infrastructure Team)
After verifying local access works:
1. Open ticket/request for infrastructure team
2. Provide: service name, port (8000), domain name
3. Infrastructure team will:
   - Configure system nginx
   - Set up SSL certificate
   - Map domain to your localhost port
   - Test and reload nginx

**⚠️ DO NOT configure nginx yourself. See [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md).**

### 6. Verify Public Access (After Infrastructure Completes)
```bash
# After infrastructure team completes nginx setup
curl https://yourdomain.com/healthz
curl https://yourdomain.com/v1/meta
```

---

## Removed: SSL/Nginx Configuration

~~Previous versions had local nginx configuration instructions.~~

**These are now handled by system-level nginx.** See:
- [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md) for architecture
- [AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md) for deployment checklist
- Contact infrastructure team for nginx/SSL issues

---

## Monitoring

### Health Checks
```bash
# Docker health status
docker compose ps

# Application logs
docker compose logs -f api
```

**Note:** Nginx logs are in system nginx, not in your docker-compose. Contact infrastructure team for nginx logs.

### Endpoints
- Health: `GET /healthz` - Always accessible via localhost (http://127.0.0.1:PORT/healthz), accessible via public domain after nginx configuration by infrastructure team
- Metadata: `GET /v1/meta` - Always accessible via localhost (http://127.0.0.1:PORT/v1/meta), accessible via public domain after nginx configuration by infrastructure team

## Updates

### Rolling Update
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Verify
curl http://yourdomain.com/healthz
```

### Rollback
```bash
# Checkout previous version
git checkout <previous-commit>

# Rebuild
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose logs api

# Check environment
docker compose exec api env | grep -E "APP_|FLOWBIZ_"

# Rebuild from scratch
docker compose down -v
docker compose up --build
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000

# Option 1: Stop conflicting process
# Option 2: Request different port assignment from infrastructure
# Update APP_PORT in .env and docker-compose.yml
```

### Nginx Issues
**DO NOT attempt to fix nginx yourself.**
- Contact infrastructure team
- Provide: service name, port, domain, error description
- Do NOT edit /etc/nginx/ files
- Do NOT restart nginx service

See [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md) for architecture details.

## Security Checklist

- [ ] Service binds to 127.0.0.1 (localhost) only
- [ ] Health endpoints (/healthz, /v1/meta) work locally
- [ ] No nginx in docker-compose.yml
- [ ] Port assignment documented and approved
- [ ] Infrastructure team notified for nginx/SSL setup
- [ ] SSL certificate managed by infrastructure (Let's Encrypt)
- [ ] Firewall managed by infrastructure
- [ ] Regular security updates (container images)
- [ ] Log monitoring enabled
- [ ] Backup strategy defined

**Note:** SSL, HSTS headers, firewall, and nginx are managed by system-level infrastructure.

## Performance

### Resource Limits
Add to docker-compose.prod.yml:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

### Scaling
```bash
# Scale API replicas
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3
```
