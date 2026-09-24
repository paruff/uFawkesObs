# Test Pyramid and Marker Taxonomy

## Overview

This document maps each BDD marker (`@smoke`, `@full`, `@chaos`) to the CI workflow that runs it, the stack profiles required, the expected runtime, and what category of scenarios belong under each marker. Contributors can decide, without reading the workflows, which marker a new scenario belongs to and what running it locally requires.

## The Five Tiers

See [`docs/TESTING_PYRAMID.md`](../docs/TESTING_PYRAMID.md) for the full
rationale and rollout history (issues #413–#417). Current state:

| Tier | Location | Status |
|---|---|---|
| **Unit** | `tests/unit/` | Static parsing, no containers. Unchanged. |
| **Integration** | `tests/integration/` | **Partially migrated to Testcontainers.** `test_otel_collector_testcontainers.py` (new file, alongside the original), `test_tempo_integration.py`, and `test_loki_integration.py`'s Loki-specific classes now self-provision their own container per test module — no `make up` needed first. The rest (`test_prometheus_scraping.py`, the original `test_otel_collector.py`, `test_grafana_integration.py`, `test_dashboards.py`, `test_alloy_and_dashboards.py`, and `test_loki_integration.py`'s `TestAlloyIntegration` class) still assume a shared stack from `ci-tests.yml`'s `docker compose up`. Track remaining files in `docs/TESTING_PYRAMID.md`'s checklist. |
| **Contract** *(new)* | `inspec/ufawkesobs-conformance/` | InSpec profile checking AGENTS.md §4 against the *actually running* stack (healthcheck status, image digest, port bindings, no anonymous volumes). Runs as `ci-tests.yml`'s `Conformance Tests (InSpec)` job on every PR, reporting only — **not yet a required branch-protection check** (needs its false-positive rate confirmed over more real runs first). Run locally with `make test-conformance`. |
| **Acceptance** | `tests/acceptance/` | pytest-bdd, `@smoke`/`@full`/`@chaos` markers — see the Marker Matrix below. Unchanged by the Testcontainers/InSpec work; still one shared running stack per scenario, which fits this tier's cross-service nature. |
| **Chaos** | `tests/acceptance/` (`@chaos` marker) | Nightly, kills/restarts real containers. Covered under Acceptance's marker taxonomy below. |

## Marker Matrix

| Marker | Workflow | CI Gate | Stack Profiles | Expected Runtime | What Belongs Here |
|--------|----------|---------|----------------|------------------|-------------------|
| `@smoke` | `Acceptance Smoke` (`.github/workflows/ci-acceptance-smoke.yml`) | Pre-merge status check. Fails the PR if any smoke test fails. | `core` only (Prometheus, Grafana, Loki, Tempo, Alertmanager, OTel Collector, Alloy) | ~2-5 minutes | Quick validation that the stack starts healthily and basic telemetry flows. Scenarios must not require external dependencies, long wait times, or container restarts. Typical: health checks, basic metrics flow, simple log queries. |
| `@full` | `Acceptance Full (Post-Merge)` (`.github/workflows/ci-acceptance-full.yml`) | Post-merge deploy gate. Blocks deployment if any full test fails. | `core` + `apps` + `dora` (full stack + telemetry generator + DORA ingestion API) | ~10-20 minutes | Comprehensive end-to-end validation. Includes DORA metric seeding, SLO validation, dashboard data checks, and multi-service integration. Scenarios exercise the complete pipeline from deployment to metric propagation. |
| `@chaos` | `Chaos Resilience (Nightly)` (`.github/workflows/ci-chaos-nightly.yml`) | Nightly gate — does not block PRs. Runs on `main` after hours. | `core` + `apps` (stack with workloads that can be killed) | ~5-10 minutes | Failure-injection scenarios. Restarts real containers, kills services, injects faults. Scenarios must be safe to run against a running stack and must not leave the stack in a broken state. Typical: container restart, metric loss, trace gap detection. |

## Workflow Details

### Acceptance Smoke (Pre-merge)

- **Trigger:** `pull_request` on `main`, `push` to `main`, `workflow_dispatch`
- **Stack:** `docker compose --profile core up -d`
- **Purpose:** Fast pre-merge validation. Runs on every PR and push to `main`.
- **Failure Impact:** PR cannot merge until all smoke tests pass.

### Acceptance Full (Post-Merge)

- **Trigger:** `push` to `main`, `workflow_dispatch`
- **Stack:** `docker compose --profile core --profile apps --profile dora up -d`
- **Purpose:** Comprehensive post-merge validation. Runs after a merge to `main`.
- **Failure Impact:** Blocks subsequent deployments via the `main-ci-guard` check.

### Chaos Resilience (Nightly)

- **Trigger:** Nightly on `main`
- **Stack:** `docker compose --profile core --profile apps up -d`
- **Purpose:** Validate resilience to container failures and fault injection.
- **Failure Impact:** Does not block PRs; failures are tracked as nightly metrics.

## Guidelines for Adding New Scenarios

1. **Determine the marker** based on the scenario's requirements:
   - Need fast feedback & no external deps? → `@smoke`
   - Exercise full pipeline including DORA metrics? → `@full`
   - Kill/restart containers? → `@chaos`

2. **Assign stack profiles** accordingly:
   - `@smoke`: `core` only
   - `@full`: `core` + `apps` + `dora`
   - `@chaos`: `core` + `apps` (no `dora` needed unless testing DORA fault injection)

3. **Update this README** with the new scenario's categorization.

4. **Add the scenario** to the appropriate `.feature` file, following the existing BDD format.

## Cross-Referencing

- `AGENTS.md` §4 rules for `tests/` — these governance rules reference the markers in this table.
- `.github/workflows/ci-acceptance-smoke.yml` — runs `-m "smoke"` scenarios.
- `.github/workflows/ci-acceptance-full.yml` — runs `-m "full"` scenarios.
- `.github/workflows/ci-chaos-nightly.yml` — runs `-m "chaos"` scenarios.
