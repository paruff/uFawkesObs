---
paths:
  - scripts/**
---

# scripts/ Rules

- `set -euo pipefail` at the top of every **bash** (`#!/bin/bash`) script.
- `set -eu` for **POSIX** (`#!/bin/sh`) scripts — `pipefail` is undefined in
  POSIX sh (shellcheck SC3040), and dash (`/bin/sh` on Debian, Ubuntu and the
  deploy host) aborts on it with "Illegal option" before the script runs at
  all. macOS `/bin/sh` is bash in POSIX mode and accepts it, so this breakage
  passes local testing and only surfaces on a real target. Guard any pipeline
  whose failure matters explicitly instead.
- `shellcheck` must pass on all scripts — it runs in CI's Pre-flight Checks and
  as a pre-commit hook; install the binary locally (`brew install shellcheck`).
- No hardcoded container names — read from `compose.yaml` or environment variables.
- Health check scripts must exit non-zero on failure.
