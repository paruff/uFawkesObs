#!/bin/sh
# Runs the DORA metrics compute batch job on a fixed interval, pushing
# results to the Prometheus pushgateway. metrics.py is a one-shot CLI
# (see ADR-007 amendment — push-based, not a scrape target); this loop
# is what turns it into a long-running service (issue #205).
set -eu

: "${DATABASE_URL:?Set DORA_POSTGRES_URL in .env (see .env.example)}"
: "${PUSHGATEWAY_URL:?Set PUSHGATEWAY_URL}"

WINDOW_DAYS="${DORA_COMPUTE_WINDOW_DAYS:-30}"
INTERVAL_SECONDS="${DORA_COMPUTE_INTERVAL_SECONDS:-3600}"

echo "dora-compute starting (window=${WINDOW_DAYS}d, interval=${INTERVAL_SECONDS}s)"

while true; do
    if python -m compute.metrics --window "$WINDOW_DAYS" --pushgateway "$PUSHGATEWAY_URL"; then
        date +%s >/tmp/dora-compute-heartbeat
    else
        echo "dora-compute cycle failed, will retry next interval" >&2
    fi
    sleep "$INTERVAL_SECONDS"
done
