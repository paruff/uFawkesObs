#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

trim_whitespace() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "${value}"
}

strip_surrounding_quotes() {
  local value="$1"
  if [ "${#value}" -ge 2 ]; then
    case "${value}" in
      \"*\") value="${value:1:${#value}-2}" ;;
      \'*\') value="${value:1:${#value}-2}" ;;
    esac
  fi
  printf '%s' "${value}"
}

read_env_password() {
  local line key raw_value

  [ -f "${ENV_FILE}" ] || return 1

  while IFS= read -r line || [ -n "${line}" ]; do
    line="${line%$'\r'}"
    case "${line}" in
      ''|[[:space:]]*'#'*) continue ;;
    esac

    key="$(trim_whitespace "${line%%=*}")"
    [ "${key}" = "GRAFANA_ADMIN_PASSWORD" ] || continue

    raw_value="${line#*=}"
    raw_value="$(trim_whitespace "${raw_value}")"
    strip_surrounding_quotes "${raw_value}"
    return 0
  done < "${ENV_FILE}"

  return 1
}

GRAFANA_ADMIN_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-}"

if [ -z "${GRAFANA_ADMIN_PASSWORD}" ]; then
  GRAFANA_ADMIN_PASSWORD="$(read_env_password || true)"
fi

export GRAFANA_ADMIN_PASSWORD

case "${GRAFANA_ADMIN_PASSWORD}" in
  ''|admin|changeme|REPLACE_ME_set_a_real_password_here)
  cat <<'EOF'
❌ Refusing to start: GRAFANA_ADMIN_PASSWORD is missing or insecure.
Set a non-default Grafana admin password before starting the stack.

Remediation:
  cp .env.example .env
  $EDITOR .env
EOF
  exit 1
  ;;
esac

echo "✅ Environment check passed: GRAFANA_ADMIN_PASSWORD is set."
