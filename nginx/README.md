# Nginx Configuration Reference

## ⚠️ IMPORTANT: DO NOT USE IN DOCKER-COMPOSE

This directory contains nginx configuration **reference templates only**.

These configurations are **NOT used** in this project's docker-compose files.

## Purpose

This directory serves as:
1. **Reference** for infrastructure team when configuring system-level nginx
2. **Documentation** of recommended security headers and proxy settings
3. **Historical context** for the architecture decision to use system-level nginx

## Architecture

This project follows the **system-level nginx** architecture described in [../docs/ADR_SYSTEM_NGINX.md](../docs/ADR_SYSTEM_NGINX.md):

- This service binds to `127.0.0.1:PORT` (localhost only)
- System nginx (managed by infrastructure team) handles:
  - Public routing
  - SSL/TLS termination
  - Security headers
  - Domain mapping

## Files in This Directory

### `templates/default.conf.template`
Reference template showing recommended nginx proxy configuration.

**Note:** This template is for reference only. The actual nginx configuration is managed by the infrastructure team at the system level (`/etc/nginx/sites-available/`).

### `snippets/security_headers.conf`
Example security headers that should be included in the system nginx configuration.

**Note:** Security headers are configured by the infrastructure team in system nginx, not in this project.

## For Developers

**DO NOT:**
- ❌ Add nginx service to docker-compose.yml
- ❌ Mount these configs in docker-compose
- ❌ Attempt to run nginx in your service
- ❌ Edit system nginx configs on VPS

**DO:**
- ✅ Ensure your service binds to localhost (127.0.0.1)
- ✅ Implement health endpoints (/healthz, /v1/meta)
- ✅ Document your port in PROJECT_CONTRACT.md
- ✅ Coordinate with infrastructure team for nginx setup

## For Infrastructure Team

When configuring system nginx for this service:

1. Use configs in `/etc/nginx/sites-available/`
2. Reference the templates in this directory
3. Map domain to service's localhost port
4. Include security headers
5. Configure SSL with Let's Encrypt
6. Test and reload nginx

See [../docs/ADR_SYSTEM_NGINX.md](../docs/ADR_SYSTEM_NGINX.md) for complete architecture details.

## Why Keep This Directory?

We keep this directory because:
- Provides reference for infrastructure team
- Documents security best practices
- Shows recommended nginx configuration
- Maintains backward compatibility with existing documentation

However, these configs are **NOT actively used** in docker-compose deployments.

## Questions?

See:
- [../docs/ADR_SYSTEM_NGINX.md](../docs/ADR_SYSTEM_NGINX.md) - Architecture overview
- [../docs/AGENT_NEW_PROJECT_CHECKLIST.md](../docs/AGENT_NEW_PROJECT_CHECKLIST.md) - Deployment process
- [../docs/AGENT_BEHAVIOR_LOCK.md](../docs/AGENT_BEHAVIOR_LOCK.md) - Rules and constraints
