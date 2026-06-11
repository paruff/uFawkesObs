---
name: lang-shell
description: "Shell/Bash and Makefile toolchain: shellcheck, shfmt, make targets, bash 3.2 compatibility rules. Use when writing or reviewing shell scripts, Makefiles, or bash automation in the fawkes scripts/ directory."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesAI
---

# Skill: Language — Shell / Bash / Makefile

## Toolchain Reference

| Gate         | Tool       | Command                      | Config file     |
| ------------ | ---------- | ---------------------------- | --------------- |
| Lint         | shellcheck | `shellcheck scripts/**/*.sh` | `.shellcheckrc` |
| Format       | shfmt      | `shfmt -w -i 2 scripts/`     | none            |
| Make dry-run | make       | `make -n [target]`           | `Makefile`      |

## Compatibility Rule (Critical for fawkes)

All shell scripts must be **bash 3.2 compatible** — this is macOS's default bash version.

**Banned bash 4+ features:**

- `mapfile` / `readarray` — use `while IFS= read -r` loop instead
- Associative arrays (`declare -A`) — use parallel indexed arrays or a Python script
- `|&` pipe syntax — use `2>&1 |` instead
- `${var,,}` / `${var^^}` case conversion — use `tr` or `awk`

## Script Standards

Every script must begin with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e` — exit on error
- `set -u` — exit on undefined variable
- `set -o pipefail` — exit on pipe failure

Error messages go to stderr: `echo "ERROR: message" >&2`

## Makefile Standards

```makefile
# Always declare phony targets
.PHONY: dev-up dev-down check-deps

# Each target must have a comment for `make help`
## dev-up: Spin up local k3d cluster (~20 min)
dev-up:
 @echo "Starting fawkes local cluster..."
 scripts/dev-up.sh

## help: List available make targets
help:
 @grep -E '^##' Makefile | sed 's/## //'
```

Required targets in fawkes Makefile:

- `check-deps` — verify prerequisites are installed
- `dev-up` — spin up local k3d cluster
- `dev-down` — tear down cluster
- `dev-status` — print service URLs and credentials
- `preflight` — run all pre-commit checks

## CI Gate Commands

```yaml
- name: Shellcheck
  run: |
    find scripts/ -name "*.sh" -exec shellcheck -S warning {} \;

- name: Shfmt check
  run: |
    shfmt -d -i 2 scripts/
```

## Common Patterns

**Safe directory traversal (bash 3.2 compatible):**

```bash
while IFS= read -r -d '' file; do
  echo "Processing: $file"
done < <(find . -name "*.sh" -print0)
```

**Check command exists:**

```bash
command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found" >&2; exit 1; }
```

**Retry with backoff:**

```bash
for i in 1 2 3 4 5; do
  command && break || { echo "Attempt $i failed, retrying..."; sleep $((i * 2)); }
done
```
