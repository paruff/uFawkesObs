#!/usr/bin/env bash
# set-grafana-folder-descriptions.sh — label dashboard folders so a new
# user can tell at a glance which are maintained vs legacy.
#
# Folder descriptions live in Grafana's own database (./data/grafana),
# not in version-controlled dashboard JSON, so they don't survive a
# fresh `make init` on a clean machine. Idempotent -- safe to re-run.
#
# Requires: GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD (from .env),
# Grafana already up and healthy (run after `make up`).

set -euo pipefail

GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"

if [[ -z "${GRAFANA_ADMIN_USER:-}" || -z "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
  echo "GRAFANA_ADMIN_USER and GRAFANA_ADMIN_PASSWORD must be set (see .env)" >&2
  exit 1
fi

set_folder_description() {
  local title="$1"
  local description="$2"
  local uid
  uid="$(curl -sf -u "${GRAFANA_ADMIN_USER}:${GRAFANA_ADMIN_PASSWORD}" \
    "${GRAFANA_URL}/api/folders" \
    | python3 -c "import json,sys; print(next((f['uid'] for f in json.load(sys.stdin) if f['title']=='${title}'), ''))")"

  if [[ -z "$uid" ]]; then
    echo "⚠️  Folder '${title}' not found, skipping" >&2
    return 0
  fi

  curl -sf -X PUT -u "${GRAFANA_ADMIN_USER}:${GRAFANA_ADMIN_PASSWORD}" \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"${title}\",\"version\":1,\"overwrite\":true,\"description\":\"${description}\"}" \
    "${GRAFANA_URL}/api/folders/${uid}" > /dev/null
  echo "✅ ${title}: description set"
}

set_folder_description "Platform" \
  "Maintained dashboards -- the current, actively-developed set. New dashboards go here."
set_folder_description "Services" \
  "Maintained dashboards -- per-service golden-signal views, keyed by the \$service template variable."
set_folder_description "Application" \
  "LEGACY -- superseded by Platform where scope overlaps (see docs/KNOWN_LIMITATIONS.md). Not actively maintained. New dashboards belong in Platform or Services instead."
