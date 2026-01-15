# flowbiz-infra-n8n Blueprint

> Goal: run n8n as an integration-only runtime, separated from FlowBiz core, with clear webhook/callback/audit contracts, secure secrets handling, and repeatable ops.

## 1) Repository Scope
- Purpose: host n8n runtime, workflow templates, bridge API, and ops tooling only.
- Out of scope: business/domain logic, source-of-truth state, long-term data storage.

## 2) High-Level Architecture
- FlowBiz Services (platform/clients) trigger jobs → Bridge API → n8n workflow → callback to FlowBiz.
- n8n is an external runner ("agent runtime extension"), not the system brain.
- Data truth and authorization remain in FlowBiz services; n8n handles orchestration/integration.

## 3) Integration Contracts (must not drift)
### 3.1 Webhook (FlowBiz → n8n)
- Endpoint: POST /v1/jobs
- Payload: job_id, client_id, workflow_key, inputs (object), callback_url, priority (1-10, default 5), timeout_seconds (default 300), metadata (object).
- Response: job_id, status(pending|running|success|failed|cancelled), message, accepted_at, estimated_completion.
- Validation: reject unknown workflow_key; enforce max timeout; rate-limit per client_id.

### 3.2 Callback (n8n → FlowBiz)
- Endpoint: POST {callback_url}
- Payload: job_id, status(success|failed), outputs, error_code, error_message, audit[], started_at, completed_at, execution_id.
- Audit entry: timestamp, action, node_name, details, duration_ms.
- Security: HMAC signature with shared secret; reject if missing/invalid; include execution_id for trace.

### 3.3 Audit / Trace
- Log for every job: who (client_id, metadata.user_id), when, workflow_key, status, error_code/message, audit trail, duration.
- Retention: >=90 days prod (1 year for financial-grade workflows).
- Store centrally (DB/Log service), not inside n8n database only.

## 4) Runtime & Deploy
- Separate repo: avoids secret leakage and decouples release cadence from AI core.
- Docker Compose stacks:
  - dev: api + n8n + postgres + redis (localhost-bound)
  - prod override: no bind-to-all, resource limits, pruning, basic auth enabled
- Bindings: services listen on 127.0.0.1; public ingress via external nginx (see ADR_SYSTEM_NGINX.md).

## 5) Directory Layout (target)
- apps/api: FastAPI bridge (`/healthz`, `/v1/meta`, `/v1/jobs`, `/v1/callbacks`).
- packages/core: config, logging, schemas (job, callback, health, error).
- workflows/templates: n8n workflow JSON templates (no secrets).
- workflows/registry.json: metadata for workflow_key validation.
- scripts: import/export workflows, backup/restore, kill-switch.
- security: secrets-policy, access-model, audit requirements.
- docs: contracts, runbook, architecture, existing ADRs.
- nginx: security headers and templates for edge.

## 6) Security Controls
- Secrets never in Git; use n8n credential store + env vars (vault later).
- Enable n8n basic auth; restrict UI to VPN/internal.
- Webhook/callback signatures (HMAC); rotate secrets; reject unsigned calls.
- Rate limit per client_id; abuse protection.
- Kill-switch: disable specific workflow or stop n8n container quickly.

## 7) Operational Runbook (essentials)
- Bootstrap: copy .env.example → .env; docker compose up; create initial admin and credentials in n8n UI.
- Import workflows: scripts/import-workflows.sh (reads templates, pushes via n8n API).
- Export workflows: scripts/export-workflows.sh (backup to templates/ with timestamps).
- Backup: postgres dump + n8n data volume snapshot; restore scripts for disaster recovery.
- Monitoring: health checks on api and n8n, alert on callback failure rate, job latency, and execution errors.

## 8) Phase Plan
- Phase 1: scaffold bridge endpoints, registry.json, one pilot workflow template, dev stack running, basic callback.
- Phase 2: job status store (redis), audit log persistence, kill-switch, tests for jobs/callbacks.
- Phase 3: security hardening (HMAC, rate limits), pruning, backups, monitoring/alerts, docs completion.

## 9) Non-Negotiables
- n8n is not source-of-truth; state/events live in FlowBiz services.
- No secrets or business logic hardcoded in workflows; credentials via n8n store.
- Every job emits audit trail and is traceable end-to-end.
- Graceful degradation: if n8n down, core FlowBiz still runs (treat as optional extension in early phases).

## 10) MVP Definition (pass/fail)
- Bridge API up with /healthz, /v1/meta, /v1/jobs, /v1/callbacks.
- n8n container reachable; one workflow template runs E2E using webhook+callback.
- Audit log captured per job; callback signature verification in place.
- Kill-switch works; no secrets in repo; docs present.

## 11) PR Plan (3 Phases)

### Phase 1: Foundation
- PR-1 `feat: add job and callback schemas` — Pydantic models (`JobRequest`, `JobResponse`, `JobCallback`, `AuditEntry`).
- PR-2 `feat: add jobs endpoint` — `POST /v1/jobs`, validate `workflow_key` from registry.
- PR-3 `feat: add callbacks endpoint` — `POST /v1/callbacks/n8n`, receive results from n8n.
- PR-4 `feat: add workflow registry and first template` — `workflows/registry.json` + pilot template (e.g., `tiktok_live_helper.json`).
- PR-5 `infra: add n8n docker compose stack` — n8n + postgres + redis in compose; config update for n8n URLs.

### Phase 2: Integration
- PR-6 `feat: add job status tracking with redis` — job state store + `GET /v1/jobs/{job_id}/status`.
- PR-7 `feat: add audit log persistence` — store audit trail per job (DB/log service).
- PR-8 `feat: add kill-switch mechanism` — `scripts/kill-switch.sh` + `POST /v1/jobs/{job_id}/cancel` + deactivate workflow via n8n API.
- PR-9 `test: add jobs and callbacks integration tests` — cover happy/error paths.
- PR-10 `feat: add second workflow template` — e.g., `tiktok_media_helper.json` or `content_pipeline.json`.

### Phase 3: Production Ready
- PR-11 `security: add HMAC signature validation` — verify callback signatures; add `callback_signing_secret` config.
- PR-12 `security: add rate limiting per client` — rate limit `/v1/jobs` by `client_id`.
- PR-13 `ops: add backup and restore scripts` — DB dumps + workflow import/export scripts.
- PR-14 `infra: add production docker-compose overrides` — resource limits, pruning, no dev volumes, hardened settings.
- PR-15 `docs: complete contracts, runbook, and security docs` — `docs/CONTRACTS.md`, `docs/RUNBOOK.md`, `security/SECRETS_POLICY.md`, `security/ACCESS_MODEL.md`.

### Dependency Graph
```
Phase 1:  PR-1 ──┬──► PR-2 ──┬──► PR-5
         │    │   │
         │    └──► PR-3 ──┘
         │
         └──► PR-4 ───► PR-2

Phase 2:  PR-5 ──► PR-6 ──► PR-7
        │
        └──► PR-8
      PR-2,3 ──► PR-9
      PR-4 ──► PR-10

Phase 3:  PR-3 ──► PR-11
      PR-2 ──► PR-12
      PR-5 ──► PR-13, PR-14
      All ──► PR-15
```
