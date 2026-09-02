#!/usr/bin/env bash
set -euo pipefail

WAIT_TIMEOUT="${WAIT_TIMEOUT:-120}"
WAIT_INTERVAL="${WAIT_INTERVAL:-2}"
CURL_CONNECT_TIMEOUT="${CURL_CONNECT_TIMEOUT:-5}"
CURL_MAX_TIME="${CURL_MAX_TIME:-10}"
WAIT_CONTEXT="${WAIT_CONTEXT:-host}"

readonly WAIT_TIMEOUT WAIT_INTERVAL CURL_CONNECT_TIMEOUT CURL_MAX_TIME WAIT_CONTEXT

validate_positive_integer() {
  local value="$1"
  local variable_name="$2"

  if ! [[ "${value}" =~ ^[0-9]+$ ]] || (( value <= 0 )); then
    echo "❌ ${variable_name} must be a positive integer (seconds), got: ${value}"
    exit 1
  fi
}

if [[ "${WAIT_CONTEXT}" == "compose" ]]; then
  SERVICES=(
    "Prometheus|http://prometheus:9090/-/healthy"
    "Grafana|http://grafana:3000/api/health"
    "Loki|http://loki:3100/ready"
    "Tempo|http://tempo:3200/ready"
    "Alloy|http://alloy:12345/-/ready"
    "OTel Collector|http://otel-collector:8888/metrics"
    "Alertmanager|http://alertmanager:9093/-/healthy"
  )
else
  SERVICES=(
    "Prometheus|http://localhost:9090/-/healthy"
    "Grafana|http://localhost:3000/api/health"
    "Loki|http://localhost:3100/ready"
    "Tempo|http://localhost:3200/ready"
    "Alloy|http://localhost:12345/-/ready"
    "OTel Collector|http://localhost:8888/metrics"
    "Alertmanager|http://localhost:9093/-/healthy"
  )
fi
readonly SERVICES

# Mutable readiness state tracked across polling iterations.
#
# A space-delimited string used as a set, not `declare -A`. The associative
# array was this script's only Bash 4 dependency, and it made the script
# refuse to run on macOS, whose system Bash is 3.2 -- including on the deploy
# host itself (DEPLOY_PATH is a /Users/... path). deploy.yml gates every
# deploy and every rollback on this script, so on such a host the health check
# could never pass and every deploy would roll back. It exits 1 when it cannot
# run, so this failed safe rather than silently reporting healthy, but the
# deploy path was unusable. Service names are single tokens, so the
# surrounding-space membership test is unambiguous.
SERVICE_READY_NAMES=""

service_is_marked_ready() {
  case " ${SERVICE_READY_NAMES} " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

is_service_ready() {
  local url="$1"
  curl -fsS --connect-timeout "${CURL_CONNECT_TIMEOUT}" --max-time "${CURL_MAX_TIME}" "${url}" >/dev/null 2>&1
}

main() {
  local start_time deadline now elapsed
  local all_ready
  local service name url service_now_ready

  validate_positive_integer "${WAIT_TIMEOUT}" "WAIT_TIMEOUT"
  validate_positive_integer "${WAIT_INTERVAL}" "WAIT_INTERVAL"

  start_time=$(date +%s)
  deadline=$((start_time + WAIT_TIMEOUT))
  echo "Waiting for core observability services (timeout: ${WAIT_TIMEOUT}s)"

  while true; do
    all_ready=true

    for service in "${SERVICES[@]}"; do
      name="${service%%|*}"
      url="${service#*|}"

      if service_is_marked_ready "${name}"; then
        continue
      fi

      service_now_ready=false
      if is_service_ready "${url}"; then
        SERVICE_READY_NAMES="${SERVICE_READY_NAMES} ${name}"
        service_now_ready=true
      else
        all_ready=false
      fi

      now=$(date +%s)
      elapsed=$((now - start_time))

      if [[ "${service_now_ready}" == "true" ]]; then
        echo "✅ ${name} healthy (${elapsed}s)"
      fi

      if (( now >= deadline )); then
        all_ready=false
        break
      fi
    done

    now=$(date +%s)
    elapsed=$((now - start_time))

    if [[ "${all_ready}" == "true" ]]; then
      echo "========================================"
      echo "✅ All core services are healthy (${elapsed}s)"
      echo "========================================"
      exit 0
    fi

    if (( now >= deadline )); then
      echo "========================================"
      for service in "${SERVICES[@]}"; do
        name="${service%%|*}"
        if ! service_is_marked_ready "${name}"; then
          echo "❌ ${name} not healthy (${elapsed}s)"
        fi
      done
      echo "❌ Timeout waiting for services after ${WAIT_TIMEOUT}s"
      echo "========================================"
      exit 1
    fi

    sleep "${WAIT_INTERVAL}"
  done
}

main "$@"
