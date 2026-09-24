#!/bin/bash
# PreToolUse hook (Bash tool): blocks any command that brings up the compose
# stack on a REMOTE host directly (e.g. `ssh <host> 'docker compose ... up'`),
# bypassing deploy.yml's reviewed pipeline (check-env, healthcheck wait,
# post-deploy verification, auto-rollback — see the gitops-reconcile skill).
# `docker compose up` run locally (no ssh) is unaffected.
set -euo pipefail

input="$(cat)"
command=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
print(data.get("tool_input", {}).get("command", ""))
')

if [ -z "$command" ]; then
  exit 0
fi

if printf '%s\n' "$command" | grep -qiE 'ssh[[:space:]].*docker([[:space:]]|-)compose.*\bup\b'; then
  echo "BLOCKED: this runs 'docker compose up' on a remote host over SSH," >&2
  echo "bypassing deploy.yml's reviewed pipeline (env checks, health waits," >&2
  echo "post-deploy verification, auto-rollback on failure)." >&2
  echo "" >&2
  echo "Push the change to main and let GitOps reconciliation deploy it," >&2
  echo "or re-run the 'GitOps Reconciliation Deploy' workflow instead." >&2
  echo "See .agents/skills/gitops-reconcile/SKILL.md." >&2
  exit 2
fi

exit 0
