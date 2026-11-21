#!/usr/bin/env bash
# Verify config/tempo/tempo.yaml with the pinned image. -config.verify exits
# non-zero on any warning, so tolerate only the intentional MCP-enabled one (#747).
set -euo pipefail
cd "$(dirname "$0")/.."

image=$(yq -r '.services["tempo"].image' compose.yaml)
rc=0
out=$(docker run --rm -v "$PWD/config/tempo/tempo.yaml:/etc/tempo.yaml" "$image" \
  -config.file=/etc/tempo.yaml -config.verify=true 2>&1) || rc=$?
echo "$out"
[ "$rc" -eq 0 ] && exit 0

unexpected=$(echo "$out" | grep -v -E 'CONFIGURATION WARNINGS|MCPServer.Enabled' | grep -v '^[[:space:]]*$') || true
if [ -n "$unexpected" ]; then
  echo "tempo config invalid" >&2
  exit 1
fi
