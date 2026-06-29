# CI Fix Report — PR #137

## Summary

| Field | Value |
|---|---|
| PR | [#137: feat/acceptance-test-scaffolding](https://github.com/paruff/uFawkesObs/pull/137) |
| Branch | `feat/acceptance-test-scaffolding` |
| Base | `main` |
| Fix Commits | `9813a3d` |

## Changes Made

### 1. `config/prometheus/rules/ai-rules.yml` — PromQL syntax fix

**Before:**
```yaml
- record: ai:suggestion_acceptance_rate:ratio
  expr: |
    0
    or vector(0)
```

**After:**
```yaml
- record: ai:suggestion_acceptance_rate:ratio
  expr: vector(0)
```

**Why:** The `or` operator in PromQL requires both operands to be instant vectors. `0` is a scalar, not a vector. The expression `0 or vector(0)` was invalid and caused:
- **Validate Configs** failure: `promtool check config` rejected it with "set operator 'or' not allowed in binary scalar expression"
- **Compose Smoke** failure: Prometheus v3.5.4 couldn't start, causing the healthcheck to fail

`vector(0)` is the correct expression for a placeholder "always zero" recording rule.

### 2. `.github/workflows/ci-pipeline.yml` — Added `issues: write` permission

**Before:**
```yaml
permissions:
  contents: read
  pull-requests: write
  security-events: write
```

**After:**
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
  security-events: write
```

**Why:** The reusable preflight workflow (`reusable-preflight.yml@v1.1.0`) posts a PR size warning comment via the GitHub Issues API (`POST /repos/{owner}/{repo}/issues/{id}/comments`), which requires the `issues: write` permission scope. Only `pull-requests: write` was configured. This 403 only manifested on large PRs (>400 lines) because that's the only condition that triggers the comment. Previous smaller PRs never hit this code path.

## Validation Results

All 25 CI checks on the latest commit (`9813a3d`) pass:

| Check Group | Result |
|---|---|
| CI (Validate) | ✅ SUCCESS |
| CI Quality (Supply Chain, Validate Configs, PR Size) | ✅ SUCCESS |
| CI Pipeline (Pre-flight → Lint → Security → Build → Tests → Complete) | ✅ SUCCESS |
| CI Tests (Unit, Compose Smoke, Integration, Golden Path) | ✅ SUCCESS |
| CodeQL | ✅ SUCCESS |
| Trivy | ✅ SUCCESS |
| GitGuardian | ✅ SUCCESS |

### Fixed Checks (from initial failure to success)

| Check | Before | After | Cause |
|---|---|---|---|
| Pre-flight / Pre-flight Checks | ❌ FAILURE | ✅ SUCCESS | Added `issues: write` permission |
| Validate Configs | ❌ FAILURE | ✅ SUCCESS | Fixed PromQL in ai-rules.yml |
| Compose Smoke | ❌ FAILURE | ✅ SUCCESS | Fixed PromQL (Prometheus starts) |
| Pipeline Complete | ❌ FAILURE | ✅ SUCCESS | All upstream jobs pass |
| PR Size | ❌ FAILURE | ✅ SUCCESS | `large-pr-approved` label applied (human) |

## Remaining Risks

| Risk | Mitigation |
|---|---|
| PR size (1506+20 lines) exceeds 400-line limit | `large-pr-approved` label applied by maintainer. Future PRs should be smaller. |
| Config validation uses `prom/prometheus:v2.55.1` promtool while compose.yaml runs v3.5.4 | Version mismatch pre-dates this PR. PromQL validated by both tools. |
