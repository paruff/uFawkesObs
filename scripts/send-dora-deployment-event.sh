#!/usr/bin/env bash
# ============================================================================
# send-dora-deployment-event.sh — emit a real deployment event to dora-api
# ----------------------------------------------------------------------------
# Called by deploy.yml on the deploy target host (where dora-api is
# co-located per compose.yaml), once per deploy/rollback outcome. This is
# the fix for #267: deploy.yml never sent any deployment event, so
# Deployment Frequency, Lead Time, and FDRT recording rules had nothing to
# compute from.
#
# Best-effort: a failure here must never fail a deploy. Observability is
# not a delivery dependency.
#
# Required env: DORA_REPO, DORA_SERVICE, DORA_ENVIRONMENT, DORA_COMMIT_SHA,
#               DORA_STATUS, DORA_PIPELINE_URL
# Optional env: DORA_PR_MERGED_AT, DORA_INGESTION_URL (default localhost:8088)
# ============================================================================

set -euo pipefail

: "${DORA_REPO:?DORA_REPO is required}"
: "${DORA_SERVICE:?DORA_SERVICE is required}"
: "${DORA_ENVIRONMENT:?DORA_ENVIRONMENT is required}"
: "${DORA_COMMIT_SHA:?DORA_COMMIT_SHA is required}"
: "${DORA_STATUS:?DORA_STATUS is required}"
: "${DORA_PIPELINE_URL:?DORA_PIPELINE_URL is required}"

DORA_URL="${DORA_INGESTION_URL:-http://localhost:8088}"
DEPLOYED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

PR_MERGED_AT_FIELD=""
if [ -n "${DORA_PR_MERGED_AT:-}" ]; then
    PR_MERGED_AT_FIELD=",
  \"pr_merged_at\": \"${DORA_PR_MERGED_AT}\""
fi

PAYLOAD=$(cat <<EOF
{
  "schema_version": "1.0",
  "event_type": "deployment",
  "repo": "${DORA_REPO}",
  "service": "${DORA_SERVICE}",
  "environment": "${DORA_ENVIRONMENT}",
  "commit_sha": "${DORA_COMMIT_SHA}",
  "deployed_at": "${DEPLOYED_AT}",
  "status": "${DORA_STATUS}",
  "pipeline_url": "${DORA_PIPELINE_URL}"${PR_MERGED_AT_FIELD}
}
EOF
)

if curl -sf -X POST "${DORA_URL}/event" \
    -H "Content-Type: application/json" \
    --connect-timeout 5 --max-time 10 \
    -d "${PAYLOAD}" > /dev/null; then
    echo "[dora] deployment event sent (status=${DORA_STATUS})"
else
    echo "::warning::Failed to send DORA deployment event (non-fatal)"
fi
