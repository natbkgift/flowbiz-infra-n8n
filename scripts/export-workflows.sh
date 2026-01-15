#!/usr/bin/env bash
set -euo pipefail

STACK_CMD=${STACK_CMD:-docker compose}
OUTPUT_DIR=${OUTPUT_DIR:-workflows/templates/exports}

mkdir -p "${OUTPUT_DIR}"

${STACK_CMD} run --rm \
  n8n \
  n8n export:workflow --separate --output=/workflows/templates/exports
