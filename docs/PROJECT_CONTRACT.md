# Project Contract (Phase 1)

**Scope:** Integration-only bridge per `docs/BLUEPRINT.md` Phase 1.

## Endpoints
- POST `/v1/jobs` — Trigger job; validates `workflow_key` against `workflows/registry.json`; returns 202 with `job_id`, `status` (pending|running|success|failed|cancelled), `message`, `accepted_at`, `estimated_completion`.
- POST `/v1/callbacks/n8n` — Receive n8n callback payload; logs and ack (200) only in Phase 1.

## Registry
- `workflows/registry.json` is the allowlist for `workflow_key`. Any unknown key must be rejected at request validation.

## Security
- HMAC signature validation for callbacks is required in production when `CALLBACK_SIGNING_SECRET` is set; in development it may be absent and requests are accepted with a warning.

## Anti-Scope (Phase 1 exclusions)
- No n8n API control (enable/disable workflows) yet.
- No job status database or Redis state tracking yet.
- No forwarding of callbacks to FlowBiz services yet (logging/ack only).

## Testing & Linting
- Required commands: `ruff check .` and `pytest`.
