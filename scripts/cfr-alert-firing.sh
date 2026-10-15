#!/usr/bin/env bash
# Print how many DORACFRRegressionRollback series are firing in Prometheus.
# Usage: cfr-alert-firing.sh [prometheus-url]
# Fails (non-zero) if Prometheus is unreachable: an unreadable alert state must
# never be read as "all clear" or "roll back".
set -euo pipefail

url="${1:-http://localhost:9090}"
query='ALERTS{alertname="DORACFRRegressionRollback",alertstate="firing"}'

curl -fsS --max-time 10 --get --data-urlencode "query=${query}" \
  "${url}/api/v1/query" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="success"; print(len(d["data"]["result"]))'
