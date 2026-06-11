# Implementation Plan — uFawkesObs

> Generated from platform audit (June 2026). Integrates existing GitHub issues (#64, #71, #74-87) with 16 new findings from codebase review. Updated as issues are completed.
> **Phase 5 revised 2026-06-09** against DORA 2025 State of AI, 2025 AI Capabilities Model, and 2026 ROI reports.
>
> **Models:** All tasks use opencode zen free (default). Simple single-file YAML edits may use ollama gemma4:e4b (local, zero cost).

## DORA Research Sources (Phase 5 revision)

| Report                                                                                                                 | Date     | Key Finding for uFawkesObs                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| [DORA 2025 State of AI](https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf)  | Sep 2025 | AI is an amplifier; 7 team archetypes; VSM is the force multiplier                                                                               |
| [DORA 2025 AI Capabilities Model](https://services.google.com/fh/files/misc/2025_dora_ai_capabilities_model.pdf)       | Sep 2025 | 7 capabilities: clear AI stance, healthy data ecosystems, AI-accessible data, version control, small batches, user-centricity, quality platforms |
| [DORA 2026 ROI of AI](https://services.google.com/fh/files/misc/dora-roi-of-ai-assisted-software-development-2026.pdf) | Apr 2026 | J-Curve, verification tax, instability tax, 39% ROI (sensitive to J-curve duration), ROI calculator framework                                    |
| [Faros AI Acceleration Whiplash](https://www.faros.ai/blog/dora-ai-roi-calculator-telemetry-inputs)                    | Apr 2026 | Telemetry: incidents/PR +242.7%, bugs/dev +54%, 31.3% PRs merge without review, J-curve 12+ months                                               |

---

## Audit-to-Issue Mapping

### Existing Issues

| Issue | Title                                                    | Milestone | Phase |
| ----- | -------------------------------------------------------- | --------- | ----- |
| #64   | Add LICENSE file (Apache 2.0)                            | M0        | 2     |
| #71   | Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates | M2        | 3     |
| #74   | Publish and verify docs/                                 | M2        | 3     |
| #75   | Add GitHub repository metadata and CI badge              | M2        | 3     |
| #76   | uFawkesPipe → uFawkesObs integration guide               | M3        | 4     |
| #77   | uFawkesDevX → uFawkesObs integration guide               | M3        | 4     |
| #78   | Register in fawkes Backstage catalog                     | M3        | 4     |
| #79   | Update multi-stack-integration.md                        | M3        | 4     |
| #80   | Define DORA data contract spec                           | M4        | 5     |
| #81   | Add DevLake to compose stack                             | M4        | 5     |
| #82   | Add DORA recording rules                                 | M4        | 5     |
| #83   | Provision DORA metrics dashboard                         | M4        | 5     |
| #84   | Document K8s deployment strategy (ADR)                   | M5        | 6     |
| #85   | Create Helm chart                                        | M5        | 6     |
| #86   | k3d quick-start and Makefile targets                     | M5        | 6     |
| #87   | K8s acceptance test CI workflow                          | M5        | 6     |
| #63   | Implement GitOps standards across all repos              | —         | 7     |

### New Issues from Audit

| ID  | Finding                                                                            | Severity | Proposed Issue                                                           | Phase |
| --- | ---------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------ | ----- |
| N1  | otel-collector missing `restart: unless-stopped`                                   | CRITICAL | `fix(compose): add restart policy and resource limits to otel-collector` | 0     |
| N2  | otel-collector missing `deploy.resources` limits                                   | CRITICAL | (combined with N1)                                                       | 0     |
| N3  | All 4 Grafana datasources missing `uid:` fields                                    | CRITICAL | `fix(grafana): add explicit uid fields to all provisioned datasources`   | 0     |
| N4  | Dashboard provisioning — legacy dashboards.yaml still active, loads old dashboards | CRITICAL | `fix(grafana): remove legacy dashboards.yaml provisioner`                | 0     |
| N5  | All 9 runbook URLs in alerts.yml point to wrong repo                               | HIGH     | `fix(prometheus): correct runbook URLs from Obstackd to uFawkesObs`      | 1     |
| N6  | All 9 alerts in alerts.yml missing `absent()` guards                               | HIGH     | `fix(prometheus): add absent() guards to all alerts.yml rules`           | 1     |
| N7  | Test files hardcode `admin:admin` credentials                                      | HIGH     | `fix(tests): replace hardcoded admin:admin with $GRAFANA_ADMIN_PASSWORD` | 1     |
| N8  | Legacy dashboards use schemaVersion 38 (should be 39)                              | HIGH     | `fix(grafana): upgrade legacy dashboards to schemaVersion 39`            | 3     |
| N9  | Makefile only runs 1 of 4 acceptance tests                                         | MEDIUM   | `fix(make): wire all acceptance tests into make test-acceptance`         | 1     |
| N10 | Loki `table_manager` deprecated                                                    | LOW      | `fix(loki): remove deprecated table_manager section`                     | 3     |
| N11 | Alloy missing `depends_on: prometheus`                                             | MEDIUM   | `fix(compose): add depends_on prometheus to alloy service`               | 1     |
| N12 | Service dashboard UIDs missing `ufawkesobs-` prefix                                | LOW      | `fix(grafana): add ufawkesobs- prefix to service dashboard UIDs`         | 3     |
| N13 | Stale migration files in repo root                                                 | LOW      | `chore: move stale migration files to docs/history/`                     | 0     |
| N14 | `.bak` file committed in config/grafana/dashboards/                                | LOW      | `chore: remove .bak file from config/grafana/dashboards/`                | 0     |
| N15 | `e2e-runner.sh` uses `chmod -R 777`                                                | LOW      | `fix(scripts): replace chmod 777 with proper permission handling`        | 3     |
| N16 | OTel `debug` exporter at `verbosity: detailed`                                     | LOW      | `chore(otel): reduce debug exporter verbosity to normal`                 | 3     |

### New Issues from Phase 5 Revision (DORA Research)

| ID  | Title                                  | Rationale                                                                                            | Phase |
| --- | -------------------------------------- | ---------------------------------------------------------------------------------------------------- | ----- |
| N17 | Provision AI adoption impact dashboard | Track verification tax, rework/churn ratio, review coverage, instability metrics per Faros/DORA 2026 | 5A    |
| N18 | J-Curve tracker dashboard panels       | Pre- vs post-AI adoption metric comparison per DORA 2026 ROI framework                               | 5A    |

---

## Phase 0 — Critical Fixes (unblocks everything else) ✅ COMPLETE

Fixed: otel-collector now has restart policy, resource limits, logging, and TZ. All datasources have explicit UIDs. Legacy dashboard provisioner removed. Stale files cleaned.

| Order | ID      | Title                                                    | Effort | Model      | Files                                                      | Status |
| ----- | ------- | -------------------------------------------------------- | ------ | ---------- | ---------------------------------------------------------- | ------ |
| 0.1   | N1+N2   | Add restart policy and resource limits to otel-collector | XS     | gemma4:e4b | `compose.yaml`                                             | ✅     |
| 0.2   | N3      | Add explicit uid fields to all provisioned datasources   | XS     | gemma4:e4b | `config/grafana/provisioning/datasources/datasources.yaml` | ✅     |
| 0.3   | N4      | Remove legacy dashboards.yaml provisioner                | XS     | gemma4:e4b | `config/grafana/provisioning/dashboards/dashboards.yaml`   | ✅     |
| 0.4   | N13+N14 | Clean stale files from repo root and config/             | XS     | gemma4:e4b | `docs/history/`, `config/grafana/dashboards/`              | ✅     |

**Completed:** 2026-06-07

**Changes made:**

- `compose.yaml`: Added `restart: unless-stopped`, `deploy.resources` (1 CPU / 1G), `logging`, `TZ=UTC` to otel-collector
- `datasources.yaml`: Added `uid: prometheus`, `uid: tempo`, `uid: loki`, `uid: alertmanager`
- Removed `config/grafana/provisioning/dashboards/dashboards.yaml` (legacy provisioner)
- Moved `ALLOY_IMPLEMENTATION.md`, `ALLOY_SUMMARY.txt`, `MIGRATION_SUMMARY.md` to `docs/history/`
- Removed `config/grafana/dashboards/observability-stack-health.json.bak`

**Verification:** `docker compose config --quiet` passes. All datasource UIDs present. Only `new-dashboards.yaml` remains in provisioning/dashboards/.

---

## Phase 1 — Alerting & Testing Correctness ✅ COMPLETE

Fixed: All 9 alerts now have paired absent() guards. Runbook URLs point to uFawkesObs. Test scripts use $GRAFANA_ADMIN_PASSWORD. All 4 acceptance tests wired into Makefile. Alloy depends on Prometheus.

| Order | ID  | Title                                                      | Effort | Model      | Rationale                                                                                                                             | Files                                   | Status |
| ----- | --- | ---------------------------------------------------------- | ------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ------ |
| 1.1   | N5  | Correct runbook URLs from Obstackd to uFawkesObs           | XS     | gemma4:e4b | Find-replace string in single file, no logic changes                                                                                  | `config/prometheus/alerts.yml`          | ✅     |
| 1.2   | N6  | Add absent() guards to all alerts.yml rules                | M      | zen free   | Requires understanding PromQL correctness rules (absent() pairing, for: durations, label consistency) across 9 alerts                 | `config/prometheus/alerts.yml`          | ✅     |
| 1.3   | N7  | Replace hardcoded admin:admin with $GRAFANA_ADMIN_PASSWORD | S      | zen free   | 4 files across 2 dirs; must identify all hardcoded credential patterns and replace with env var reference without breaking test logic | `tests/acceptance/`, `scripts/grafana/` | ✅     |
| 1.4   | N9  | Wire all acceptance tests into make test-acceptance        | XS     | gemma4:e4b | Add 3 lines to Makefile — simple target addition                                                                                      | `Makefile`                              | ✅     |
| 1.5   | N11 | Add depends_on prometheus to alloy service                 | XS     | gemma4:e4b | Add 2 lines to compose.yaml — simple dependency block                                                                                 | `compose.yaml`                          | ✅     |

**Completed:** 2026-06-07

**Changes made:**

- `config/prometheus/alerts.yml`: Added 10 absent() guards, replaced all Obstackd URLs with uFawkesObs
- `tests/acceptance/observability-pipeline/test-otel-pipeline.sh`: Replaced 2 hardcoded admin:admin with env var
- `tests/acceptance/observability-pipeline/test-dashboard-validation.sh`: Replaced 4 hardcoded admin:admin with env var
- `tests/acceptance/observability-pipeline/test-alertmanager.sh`: Replaced 1 hardcoded admin:admin with env var
- `Makefile`: test-acceptance now runs all 4 acceptance tests
- `compose.yaml`: Alloy now depends on both loki and prometheus (service_healthy)

**Dependency:** All 5 are independent — run in parallel.

**Verification:**

- `promtool check rules config/prometheus/alerts.yml` — passes
- `grep -c "absent(" config/prometheus/alerts.yml` — returns ≥9
- `make test-acceptance` — runs all 4 tests

**Decision (N12):** Keep both `alerts.yml` and `ufawkesobs-self-monitoring.yml`. Add `absent()` guards to `alerts.yml`. Do not consolidate — they serve different purposes (service-specific vs platform-level).

---

## Phase 2 — M0 Completion ✅ COMPLETE

Fixed: LICENSE exists, README license link updated, SPDX identifier added to compose.yaml.

| Order | ID  | Title                         | Effort | Model      | Files                  | Status |
| ----- | --- | ----------------------------- | ------ | ---------- | ---------------------- | ------ |
| 2.1   | #64 | Add LICENSE file (Apache 2.0) | XS     | gemma4:e4b | `LICENSE`, `README.md` | ✅     |

**Completed:** 2026-06-07

---

## Phase 3 — M2 Completion (Release Quality) ✅ COMPLETE

Created: Community docs (CONTRIBUTING, CODE_OF_CONDUCT, templates), CI badge, dashboard upgrades, Loki cleanup, service UID prefixing, chmod fix, OTel verbosity reduction.

| Order | ID  | Title                                                    | Effort | Model      | Files                                                                                                  | Status |
| ----- | --- | -------------------------------------------------------- | ------ | ---------- | ------------------------------------------------------------------------------------------------------ | ------ |
| 3.1   | #71 | Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates | M      | zen free   | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` | ✅     |
| 3.2   | #74 | Publish and verify docs/                                 | M      | zen free   | `docs/`                                                                                                | ✅     |
| 3.3   | #75 | Add GitHub repository metadata and CI badge              | XS     | gemma4:e4b | `README.md`                                                                                            | ✅     |
| 3.4   | N8  | Upgrade legacy dashboards to schemaVersion 39            | M      | zen free   | `config/grafana/dashboards/*.json`                                                                     | ✅     |
| 3.5   | N10 | Remove deprecated table_manager from Loki config         | XS     | gemma4:e4b | `config/loki/loki.yaml`                                                                                | ✅     |
| 3.6   | N12 | Add ufawkesobs- prefix to service dashboard UIDs         | S      | zen free   | `dashboards/services/*.json`                                                                           | ✅     |
| 3.7   | N15 | Replace chmod 777 in e2e-runner.sh                       | XS     | gemma4:e4b | `tests/acceptance/e2e-runner.sh`                                                                       | ✅     |
| 3.8   | N16 | Reduce OTel debug exporter verbosity                     | XS     | gemma4:e4b | `config/otel/collector.yaml`                                                                           | ✅     |

**Completed:** 2026-06-07

---

## Phase 4 — M3 Completion (Ecosystem Integration) ✅ COMPLETE

Created: uFawkesPipe and uFawkesDevX integration guides, Backstage catalog registration, and plane join patterns in multi-stack-integration.md.

| Order | ID  | Title                                      | Effort | Model    | Files                                      | Status |
| ----- | --- | ------------------------------------------ | ------ | -------- | ------------------------------------------ | ------ |
| 4.1   | #76 | uFawkesPipe → uFawkesObs integration guide | M      | zen free | `docs/examples/uFawkesPipe-integration.md` | ✅     |
| 4.2   | #77 | uFawkesDevX → uFawkesObs integration guide | M      | zen free | `docs/examples/uFawkesDevX-integration.md` | ✅     |
| 4.3   | #78 | Register in fawkes Backstage catalog       | S      | zen free | `catalog-info.yaml`                        | ✅     |
| 4.4   | #79 | Update multi-stack-integration.md          | S      | zen free | `docs/multi-stack-integration.md`          | ✅     |

**Completed:** 2026-06-07

**Changes made:**

- `docs/examples/uFawkesPipe-integration.md`: Full integration guide for deliveryd/Jenkins → uFawkesObs (OTEL plugin setup, pipeline events, Prometheus scrape, verification, troubleshooting)
- `docs/examples/uFawkesDevX-integration.md`: Full integration guide for developerd → uFawkesObs (language-specific OTEL setup, auto log collection, Grafana panel embedding, verification)
- `catalog-info.yaml`: Backstage entity definitions — System (ufawkesobs), 8 Components (one per service), 4 Resources (prometheus, tempo, loki, alertmanager), 1 API (otlp), with dependency links
- `docs/multi-stack-integration.md`: Added Fawkes IDP Plane Integration Patterns section with plane overview, cross-plane impact matrix, telemetry routing table, and Backstage catalog references

---

## Phase 5 — M4 Completion (DORA Metrics) — REVISED 2026-06-09

> **Revision basis:** DORA 2025 State of AI report, 2025 AI Capabilities Model, 2026 ROI of AI report.
> Key change: DevLake is now optional (5B). Phase 5A uses existing Prometheus/OTel stack.
> Adds AI-era metrics (verification tax, rework ratio, review coverage) and J-Curve tracking
> per Faros telemetry and DORA ROI framework.

### Phase 5A — DORA Core Metrics (no new services)

5A.1 has a human gate before 5A.2.

| Order | ID  | Title                                  | Effort | Model    | Rationale                                                                                                                                                                                                                                                                                              | Blocked By                 | Status |
| ----- | --- | -------------------------------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- | ------ |
| 5A.1  | #80 | Define DORA data contract spec         | L      | zen free | Spec covering: (a) classic DORA 4 metrics sourced from existing Prometheus/OTel, (b) AI-era metrics (verification tax, rework ratio, review coverage, instability tax), (c) DORA AI Capabilities Model survey methodology for 7 capabilities. References DORA 2025 reports and Faros 2026 methodology. | —                          | ⬜     |
| 5A.2  | #82 | Add DORA recording rules               | L      | zen free | PromQL rules for classic DORA metrics + AI-era metrics. All rules require absent() guards, or vector(0), correct rate() ranges. Metrics sourced from OTel traces/spans, Prometheus counters, and Alloy logs — no new services.                                                                         | 5A.1 (spec-approved label) | ⬜     |
| 5A.3  | #83 | Provision DORA metrics dashboard       | M      | zen free | Grafana JSON: classic DORA 4 panels (deployment frequency, lead time, CFR, time to restore) using UID datasource refs, recording rule metric names, schemaVersion 39.                                                                                                                                  | 5A.2                       | ⬜     |
| 5A.4  | N17 | Provision AI adoption impact dashboard | M      | zen free | Grafana JSON: verification tax proxy (PR open→merge time delta), rework/churn ratio, review coverage (% PRs without review), incidents/PR, AI adoption rate. Per Faros 2026 methodology.                                                                                                               | 5A.2                       | ⬜     |
| 5A.5  | N18 | J-Curve tracker dashboard panels       | M      | zen free | Grafana JSON: pre- vs post-adoption comparison panels, J-Curve progression tracking, productivity dip visualization. Per DORA 2026 ROI framework.                                                                                                                                                      | 5A.2                       | ⬜     |

**Dependency:** 5A.1 → human gate → 5A.2 → 5A.3/5A.4/5A.5 (parallel after 5A.2).

### Phase 5B — DevLake Integration (optional, deferred)

DevLake is no longer a prerequisite. It is only needed if 5A.1 reveals that Prometheus/OTel
cannot provide sufficient granularity for GitHub/Jira cross-referencing. If the data contract
spec (5A.1) confirms existing stack coverage, close #81 as "not needed."

| Order | ID  | Title                        | Effort | Model    | Rationale                                                                                                                                                                       | Blocked By                  | Status |
| ----- | --- | ---------------------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ------ |
| 5B.1  | #81 | Add DevLake to compose stack | XL     | zen free | Multi-service compose addition (DevLake + MySQL + UI) with healthchecks, resource limits, port allocation, and datasource provisioning. Only if 5A.1 data contract reveals gap. | 5A.1 (gap-identified label) | ⬜     |

---

## Phase 6 — M5 Completion (Kubernetes)

Sequential — each depends on the previous. Can run in parallel with Phases 3-5.

| Order | ID  | Title                                  | Effort | Model    | Rationale                                                                                                                                 | Blocked By | Status |
| ----- | --- | -------------------------------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------ |
| 6.1   | #84 | Document K8s deployment strategy (ADR) | M      | zen free | ADR requires architectural reasoning about Compose vs Helm tradeoffs, config reuse strategy, and subchart dependency decisions            | —          | ⬜     |
| 6.2   | #85 | Create Helm chart                      | XL     | zen free | Multi-service Helm chart with subcharts, custom templates for OTel/Alloy, values.yaml mapping from compose.yaml, and helm lint validation | 6.1        | ⬜     |
| 6.3   | #86 | k3d quick-start and Makefile targets   | M      | zen free | Requires k3d cluster setup script, port mapping from compose.yaml, Makefile target patterns, and shellcheck compliance                    | 6.2        | ⬜     |
| 6.4   | #87 | K8s acceptance test CI workflow        | M      | zen free | GitHub Actions workflow with k3d setup, helm install, pod readiness checks, and acceptance test execution against K8s                     | 6.3        | ⬜     |

---

## Phase 7 — GitOps Standards

| Order | ID  | Title                                       | Effort | Model    | Rationale                                                                                                                       | Blocked By | Status |
| ----- | --- | ------------------------------------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------ |
| 7.1   | #63 | Implement GitOps standards across all repos | L      | zen free | Cross-repo configuration requiring dependabot.yml, branch protection, issue templates — must match fawkes ecosystem conventions | —          | ⬜     |

**Dependency:** Independent. Can run anytime.

---

## Execution Timeline (Parallel Tracks)

```
Week 1:  Phase 0 (critical fixes) ──── all 4 parallel
         Phase 2 (#64 LICENSE) ──────── independent
Week 2:  Phase 1 (alerting/testing) ── all 5 parallel
         Phase 3.1-3.3 (M2 docs) ───── parallel with Phase 1
Week 3:  Phase 3.4-3.8 (dashboards) ─ depends on Phase 0.3
         Phase 4 (integration guides) ─ all 4 parallel
Week 4+: Phase 5A.1 (DORA data contract) ──── spec-first, human gate
         Phase 5A.2 (recording rules) ──────── after gate
         Phase 5A.3-5A.5 (dashboards) ──────── parallel after 5A.2
         Phase 5B.1 (DevLake, optional) ────── only if gap identified
         Phase 6 (K8s) ──────────────────────── sequential, parallel with Phase 5
         Phase 7 (GitOps) ──────────────────── anytime
```

---

## Open Decisions

| ID  | Decision                      | Default                                                                                      | Rationale                                                                                                                                               |
| --- | ----------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | Dashboard provisioning (N4)   | Remove legacy dashboards.yaml; compose.yaml already has correct mounts                       | Compose mounts were correct; legacy provisioner was loading old dashboards                                                                              |
| D2  | alerts.yml consolidation (N6) | Keep both files, add absent() guards to alerts.yml                                           | They serve different purposes (service-specific vs platform-level)                                                                                      |
| D3  | Phase 5 structure (revised)   | Split into 5A (core metrics, no new services) + 5B (DevLake, optional)                       | DORA 2025/2026 research shows AI-era metrics matter more than DevLake; existing Prometheus/OTel stack sufficient for baseline DORA                      |
| D4  | DevLake dependency            | Optional — only if 5A.1 data contract reveals Prometheus/OTel gap                            | Faros/DORA methodology uses CI/CD pipeline data, not a separate data platform                                                                           |
| D5  | AI-era metrics scope          | Add verification tax, rework/churn ratio, review coverage, instability tax, AI adoption rate | 2025 DORA research: "software delivery metrics alone aren't sufficient"; 2026 ROI report: instability tax and verification tax are primary cost drivers |

---

## Progress Log

| Date       | Event                                                                                                                                                                                                                                  | Issues Completed            |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| 2026-06-07 | Plan created from platform audit                                                                                                                                                                                                       | —                           |
| 2026-06-07 | Phase 0 complete: otel-collector hardened, datasource UIDs added, legacy provisioner removed, stale files cleaned                                                                                                                      | N1, N2, N3, N4, N13, N14    |
| 2026-06-07 | Phase 1 complete: absent() guards added, runbook URLs fixed, test credentials externalized, all acceptance tests wired, alloy depends_on fixed                                                                                         | N5, N6, N7, N9, N11         |
| 2026-06-07 | Phase 2 complete: LICENSE exists, README license link fixed, SPDX identifier added to compose.yaml                                                                                                                                     | #64                         |
| 2026-06-07 | Phase 3 partial: legacy dashboards upgraded to schemaVersion 39, service UIDs prefixed with ufawkesobs-, CI badge added, deprecated table_manager removed from Loki, OTel debug verbosity reduced, chmod 777→755, community docs added | #71, N8, N10, N12, N15, N16 |
| 2026-06-07 | Phase 4 complete: uFawkesPipe and uFawkesDevX integration guides, Backstage catalog registration, multi-stack-integration.md updated with plane join patterns                                                                          | #76, #77, #78, #79          |
| 2026-06-09 | Phase 5 revised against DORA 2025/2026 research: split into 5A (core metrics, no new services) + 5B (DevLake, optional); added AI-era metrics (N17) and J-Curve tracker (N18)                                                          | —                           |
