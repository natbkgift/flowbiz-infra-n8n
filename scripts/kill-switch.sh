#!/usr/bin/env bash
set -euo pipefail

STACK_CMD=${STACK_CMD:-docker compose}
API_BASE_URL=${N8N_API_BASE_URL:-http://127.0.0.1:5678/api/v1}
API_KEY=${N8N_API_KEY:-}
ACTION=${1:-}
TARGET=${2:-}

usage() {
  echo "Usage: $0 deactivate <workflow_key|workflow_id>" >&2
  echo "   or: $0 stop" >&2
  exit 1
}

if [[ -z "${ACTION}" ]]; then
  usage
fi

API_BASE_URL=${API_BASE_URL%/}

case "${ACTION}" in
  deactivate)
    if [[ -z "${TARGET}" ]]; then
      usage
    fi

    if [[ -z "${API_KEY}" ]]; then
      echo "ERROR: N8N_API_KEY is required to deactivate workflows." >&2
      exit 1
    fi

    export WORKFLOWS_JSON
    export WORKFLOW_TARGET

    WORKFLOW_TARGET="${TARGET}"
    WORKFLOWS_JSON=$(curl -sS -H "X-N8N-API-KEY: ${API_KEY}" "${API_BASE_URL}/workflows")

    WORKFLOW_ID=$(python - <<'PY'
import json
import os
import sys

target = os.environ.get("WORKFLOW_TARGET")
raw = os.environ.get("WORKFLOWS_JSON")

if raw is None or target is None:
    sys.exit(1)

data = json.loads(raw)
items = data.get("data") if isinstance(data, dict) else data
if not isinstance(items, list):
    sys.exit(1)

workflow_id = None
for item in items:
    if not isinstance(item, dict):
        continue
    name = item.get("name") or item.get("displayName")
    if name == target or str(item.get("id")) == target:
        workflow_id = item.get("id")
        break

if workflow_id is None:
    sys.exit(2)

print(workflow_id)
PY
)

    if [[ -z "${WORKFLOW_ID}" ]]; then
      echo "ERROR: workflow '${TARGET}' not found in n8n." >&2
      exit 2
    fi

    curl -sS -X PATCH \
      -H "X-N8N-API-KEY: ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d '{"active":false}' \
      "${API_BASE_URL}/workflows/${WORKFLOW_ID}" >/dev/null

    echo "Workflow '${TARGET}' (${WORKFLOW_ID}) deactivated via n8n API."
    ;;
  stop)
    ${STACK_CMD} stop n8n
    echo "n8n container stopped via ${STACK_CMD}."
    ;;
  *)
    usage
    ;;
esac
