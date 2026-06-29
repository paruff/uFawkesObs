# CI Diagnosis — PR #137

## Failure 1: Pre-flight / Pre-flight Checks

| Field | Value |
|---|---|
| Status | FAILURE |
| Step | PR comment via github-script |
| Evidence | `POST /repos/paruff/uFawkesObs/issues/137/comments - 403` — `Resource not accessible by integration` |
| Root Cause | The reusable workflow `reusable-preflight.yml@v1.1.0` tries to post a PR size warning via the Issues API. The GITHUB_TOKEN has `pull-requests: write` but NOT `issues: write`, which is required for the `/issues/{id}/comments` endpoint. This 403 only manifests on large PRs (>400 lines) because that's when the workflow attempts to post a warning. Previous smaller PRs didn't trigger this code path. |
| Classification | **Pipeline Failure** — CI configuration permissions |
| Confidence | HIGH |

## Failure 2: Compose Smoke

| Field | Value |
|---|---|
| Status | FAILURE |
| Step | `docker compose --profile core up -d --build` |
| Evidence | `Container prometheus Error` → `dependency failed to start: container prometheus is unhealthy` |
| Root Cause | Prometheus v3.5.4 cannot start because `config/prometheus/rules/ai-rules.yml` contains invalid PromQL. The recording rule `ai:suggestion_acceptance_rate:ratio` uses `0 or vector(0)` — the `or` operator is only valid between instant vectors, not between a scalar (`0`) and a vector. Prometheus v3 rejects this at startup. |
| Classification | **Code Failure** — PromQL syntax error |
| Confidence | HIGH |

## Failure 3: Validate Configs

| Field | Value |
|---|---|
| Status | FAILURE |
| Step | `promtool check config` |
| Evidence | `/etc/prometheus/rules/ai-rules.yml: 43:15: group "ai_capability_recording_rules", rule 4, "ai:suggestion_acceptance_rate:ratio": could not parse expression: 1:1: parse error: set operator "or" not allowed in binary scalar expression` |
| Root Cause | Same as above — invalid PromQL `0 or vector(0)` in ai-rules.yml line 43. |
| Classification | **Code Failure** — PromQL syntax error |
| Confidence | HIGH |

## Failure 4: PR Size

| Field | Value |
|---|---|
| Status | FAILURE |
| Step | `actions/github-script@v9` PR size check |
| Evidence | `❌ PR size: 1438 lines (limit: 400)` |
| Root Cause | The PR adds acceptance test scaffolding (feature files, step definitions, conftest) totaling 1438 changed lines, exceeding the 400-line limit. |
| Classification | **Pipeline Failure** — PR size gate |
| Confidence | HIGH |
| Note | Requires `large-pr-approved` label from a human maintainer. Agent cannot apply this label per AGENTS.md ("humans only"). |

## Failure 5: Pipeline Complete

| Field | Value |
|---|---|
| Status | FAILURE |
| Evidence | Cascading aggregate — depends on all other jobs |
| Root Cause | Aggregation of failures 1–4. Will pass when all upstream jobs pass. |

---

## Cascading Failures

The following jobs were SKIPPED due to upstream failures:

| Job | Skipped Because |
|---|---|
| Static Analysis | depends on preflight |
| Security Scanning | depends on lint |
| Dependency Review | depends on lint |
| Build & Validate | depends on security + dependency-review |
| Tests (aggregate) | depends on build |
| Integration Tests | depends on compose-smoke |
| Golden Path App | depends on compose-smoke |
