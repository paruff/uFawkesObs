#!/usr/bin/env bash
# Stack prerequisites for `make up`: Docker reachable, .env present, host ports free.
# Ports come from compose.yaml (the profiles `make up` starts), not a copy here.
# A port already held by a container of this compose project counts as fine.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

fail=0
bad() {
  printf '  FAIL  %s\n        fix: %s\n' "$1" "$2"
  fail=1
}

if ! docker info > /dev/null 2>&1; then
  bad "Docker is not reachable" "colima start   (Docker Desktop is not used on this machine)"
  exit 1
fi

[ -f .env ] || bad ".env is missing, so \`make up\` fails on GRAFANA_ADMIN_PASSWORD" "cp .env.example .env and set real values"

envfile=.env
[ -f .env ] || envfile=.env.example
ports=$(docker compose --env-file "$envfile" --profile core --profile apps config --format json 2> /dev/null \
  | yq -p json -r '.services[].ports[]? | .published' | sort -un)
[ -n "$ports" ] || bad "no published ports found in compose.yaml" "run: docker compose config"

for p in $ports; do
  nc -z 127.0.0.1 "$p" > /dev/null 2>&1 || continue
  if [ -n "$(docker ps -q --filter "publish=$p" --filter label=com.docker.compose.project)" ]; then continue; fi
  bad "port $p is already in use by another process" "stop it (lsof -nP -iTCP:$p -sTCP:LISTEN) or change the port in .env"
done

[ "$fail" -eq 0 ] && echo "stack prerequisites OK (Docker, .env, ports)"
exit "$fail"
