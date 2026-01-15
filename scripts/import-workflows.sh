#!/usr/bin/env bash
set -euo pipefail

STACK_CMD=${STACK_CMD:-docker compose}
TEMPLATES_DIR=${TEMPLATES_DIR:-workflows/templates}

if [ ! -d "${TEMPLATES_DIR}" ]; then
  echo "ERROR: workflow template directory \"${TEMPLATES_DIR}\" not found." >&2
  exit 1
fi

${STACK_CMD} run --rm \
  n8n \
  n8n import:workflow --separate --input=/workflows/templates
