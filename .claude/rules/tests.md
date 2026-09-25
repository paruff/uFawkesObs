---
paths:
  - tests/**
---

# tests/ Rules

- Unit tests in `tests/unit/` — validate config YAML, JSON, and conventions.
- Integration tests in `tests/integration/` — BDD-style, run against running stack.
- Acceptance tests in `tests/acceptance/` — verify the stack is observable.
- Every test must have a clear pass/fail exit code.
- Never delete failing tests to make a build pass.
- Never swallow an exception in a check, validation, or assertion without
  logging what broke (the exception itself, not just that something
  failed) — a silently-caught exception that makes a check report "no
  issue found" is indistinguishable from a check that never ran, and
  hides real bugs indefinitely. (Real incident, 2026-08-18: an
  `except Exception: pass` in an acceptance-test panel check silently
  swallowed Prometheus Pushgateway 400 errors, hiding two real bugs.)
