# Plan: adopt ruff v0.17

The pre-commit-hooks group bump moves ruff v0.16.9 to v0.17.2. The new
release adds rules (UP017, FURB162) that flag existing code, so Pre-flight
fails until the code is adjusted.

## Changes

- Replace `timezone.utc` with `datetime.UTC` (UP017), 42 auto-fixes.
- Drop `.replace("Z", "+00:00")` before `datetime.fromisoformat` (FURB162).
  Python 3.11+ parses a trailing `Z`; CI and the images run 3.12/3.13.
- Reformat with `ruff format`.

## Verification Strategy

- `ruff check .` and `ruff format --check .` at v0.17.2 report no findings.
- `pytest tests/unit` passes (681 tests), including the DORA SQLite and
  backfill tests that exercise the changed `fromisoformat` calls.
- Pre-flight and Integration Tests pass in CI.
