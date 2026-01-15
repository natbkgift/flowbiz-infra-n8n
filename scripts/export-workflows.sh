#!/usr/bin/env bash
set -euo pipefail

STACK_CMD=${STACK_CMD:-docker compose}
EXPORT_SUBDIR=${EXPORT_SUBDIR:-exports}

mkdir -p "workflows/templates/${EXPORT_SUBDIR}"

${STACK_CMD} run --rm \
  n8n \
  n8n export:workflow --separate --output="/workflows/templates/${EXPORT_SUBDIR}"
