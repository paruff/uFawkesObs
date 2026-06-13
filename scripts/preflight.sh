#!/usr/bin/env bash
# preflight.sh — preflight gate for uFawkesObs
# Run: ./scripts/preflight.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

failures=0

pass() { printf "%b\n" "${GREEN}✅ ${NC} $*"; }
warn() { printf "%b\n" "${YELLOW}⚠️  ${NC} $*"; }
fail() { printf "%b\n" "${RED}❌ ${NC} $*"; failures=$((failures + 1)); }

echo ""
echo "Running preflight checks..."
echo ""

# ── 1) Shellcheck all shell scripts ─────────────────────────────────────────

if ! command -v shellcheck >/dev/null 2>&1; then
  fail "shellcheck is required but not installed. Run: brew install shellcheck"
else
  shell_files=()
  while IFS= read -r -d '' f; do
    shell_files+=("$f")
  done < <(find . -type f -name '*.sh' \
    ! -path './.git/*' \
    ! -path './node_modules/*' \
    ! -path './vendor/*' \
    -print0)

  if [ "${#shell_files[@]}" -eq 0 ]; then
    warn "No shell scripts found."
  elif shellcheck "${shell_files[@]}"; then
    pass "shellcheck passed for ${#shell_files[@]} script(s)."
  else
    fail "shellcheck reported issues."
  fi
fi

# ── 2) AGENTS.md must have no unfilled placeholders ─────────────────────────

if [ ! -f AGENTS.md ]; then
  fail "AGENTS.md is missing."
else
  placeholder_lines="$(grep -nE '\[PLACEHOLDER[^]]*\]' AGENTS.md || true)"
  if [ -n "${placeholder_lines}" ]; then
    echo "${placeholder_lines}"
    if [ "${PREFLIGHT_ENFORCE_PLACEHOLDERS:-0}" = "1" ]; then
      fail "AGENTS.md contains unfilled [PLACEHOLDER] markers."
    else
      warn "AGENTS.md contains [PLACEHOLDER] markers (template mode). Set PREFLIGHT_ENFORCE_PLACEHOLDERS=1 to enforce."
    fi
  else
    pass "AGENTS.md contains no [PLACEHOLDER] markers."
  fi
fi

# ── 3) Required files must exist ─────────────────────────────────────────────

required_files=(
  "compose.yaml"
  "Makefile"
  ".pre-commit-config.yaml"
  ".pipeline.yml"
  "config/prometheus/prometheus.yaml"
  "config/otel/collector.yaml"
  "config/tempo/tempo.yaml"
  "config/grafana/grafana.ini"
)

for file in "${required_files[@]}"; do
  if [ -f "${file}" ]; then
    pass "${file} exists."
  else
    fail "${file} is missing."
  fi
done

# ── 4) compose.yaml must be valid YAML ──────────────────────────────────────

if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import yaml; yaml.safe_load(open('compose.yaml'))" 2>/dev/null; then
    pass "compose.yaml is valid YAML."
  else
    fail "compose.yaml is not valid YAML."
  fi
else
  warn "python3 not available, skipping YAML validation."
fi

# ── 5) No :latest tags in compose.yaml ──────────────────────────────────────

if grep -q "image: .*:latest" compose.yaml 2>/dev/null; then
  fail "compose.yaml uses :latest tags."
else
  pass "No :latest tags in compose.yaml."
fi

# ── 6) Symlinks for agent instructions ──────────────────────────────────────

required_symlinks=(
  ".github/copilot-instructions.md"
)

for link_path in "${required_symlinks[@]}"; do
  if [ ! -L "${link_path}" ]; then
    warn "${link_path} is not a symlink (optional)."
    continue
  fi
  if [ -e "${link_path}" ]; then
    pass "${link_path} exists and resolves."
  else
    fail "${link_path} is a broken symlink."
  fi
done

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
if [ "${failures}" -gt 0 ]; then
  printf "%b\n" "${RED}Preflight failed with ${failures} issue(s).${NC}"
  exit 1
fi
printf "%b\n" "${GREEN}Preflight passed.${NC}"
