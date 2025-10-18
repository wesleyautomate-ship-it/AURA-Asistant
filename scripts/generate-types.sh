#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
OUT_JSON="$ROOT_DIR/scripts/openapi.json"
OUT_TYPES="$ROOT_DIR/aura-client/src/types/api.d.ts"

echo "Exporting OpenAPI schema..."
python "$ROOT_DIR/scripts/export_openapi_min.py" "$OUT_JSON"

echo "Generating TypeScript types via openapi-typescript..."
npx --yes openapi-typescript "$OUT_JSON" --output "$OUT_TYPES"

echo "Types generated at $OUT_TYPES"
