#!/bin/bash
# Stop hook: before a Claude Code session finishes a turn, run pre-commit on
# the files it changed (modified + untracked, not ignored). A failure blocks
# the stop (exit 2) and hands the output back to Claude to fix -- the
# AI-Native SDLC "every session checks its own work before a human sees it".
#
# Same hooks as CI's required "Pre-commit Hooks" check, scoped to changed
# files so it stays fast. Skips (exit 0) when not in a git repo, pre-commit
# isn't installed, nothing changed, or Claude is already continuing because
# of this hook (stop_hook_active) -- blocking again would loop.
set -euo pipefail

input="$(cat)"
active=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    print(str(json.load(sys.stdin).get("stop_hook_active", False)).lower())
except Exception:
    print("false")
')
[ "$active" = "true" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
command -v pre-commit >/dev/null 2>&1 || exit 0
[ -f .pre-commit-config.yaml ] || exit 0

mapfile -t files < <(
  {
    git diff --name-only --diff-filter=ACMR HEAD 2>/dev/null || true
    git ls-files --others --exclude-standard
  } | sort -u
)
[ "${#files[@]}" -eq 0 ] && exit 0

if ! output=$(pre-commit run --files "${files[@]}" 2>&1); then
  {
    echo "Stop hook: pre-commit failed on this session's changed files."
    echo "Fix these before finishing (auto-fixers may already have edited files):"
    echo
    printf '%s\n' "$output" | grep -vE '\.(Passed|Skipped)$' | tail -60
  } >&2
  exit 2
fi
exit 0
