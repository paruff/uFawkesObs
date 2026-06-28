# uFawkesObs — Implementation Plan

**Version:** 1.1.0
**Date:** 2026-06-28
**Repo:** paruff/uFawkesObs
**Status:** Active

---

## Guide to Using This Plan

- This implementation plan guides the development of the uFawkesObs platform.
- Tasks are derived from the actual open issues backlog in `gh issue list`.
- Do not start any task until all its **Dependencies** are fully completed.
- Every task must be verified with automated test gates (such as `make test`) before being marked complete.
- Milestones with "P0" priority should be completed before any P1 milestone.

---

## Milestone 1 — Repository Foundation

*Theme: Establish repository structure, CI pipelines, and core architectural documentation.*

### Task M1-01: CI Pipeline Refactor

- **Description:** Migrate reusable CI workflows to uFawkesPipe.
- **Backlog Issue:** N/A (foundation)
- **Status:** ✅ DONE (PR #121 merged)
- **Details:**
  - Migrated to uFawkesPipe@v1.1.0
  - Disabled coverage gate (coverage paths don't apply to Docker Compose config repos)
  - All 225 unit tests passing consistently

### Task M1-02: Loki v2.9.10 → v3.3.2 Migration

- **Description:** Upgrade Loki from 2.9.10 to 3.3.2 with config migration.
- **Backlog Issue:** N/A (foundation)
- **Status:** ✅ DONE (PR #116 merged)
- **Details:**
  - `compose.yaml` updated to `grafana/loki:3.3.2`
  - `config/loki/loki.yaml` migrated to v3.x format (TSDB shipper, compactor, schema v13)
  - All unit tests pass including `test_loki_schema.py` v3.x checks

### Task M1-03: Grafana v10.4.5 → v12.3.7 Upgrade

- **Description:** Upgrade Grafana from 10.4.5 to 12.3.7.
- **Backlog Issue:** N/A (foundation)
- **Status:** ✅ DONE
- **Details:**
  - `compose.yaml` updated to `grafana/grafana:12.3.7`
  - All existing dashboards and provisioning configs compatible
  - 225 unit tests pass

### Task M1-04: OBS-AI-01 — Add AI Metrics Pipeline to OTel Collector

- **Description:** Add `metrics/ai` pipeline with `filter/ai` and `attributes/ai` processors.
- **Backlog Issue:** #55
- **Status:** ✅ DONE (PR #123)
- **Details:**
  - `filter/ai`: passes through `gen_ai.*`, `llm.*`, `openllmetry.*`, `ai.*` metrics with `error_mode: ignore`
  - `attributes/ai`: inserts `ai.environment=development` and `ai.platform=fawkes-idp`
  - `metrics/ai` pipeline: `receivers: [otlp]` → `[memory_limiter, filter/ai, attributes/ai, batch]` → `exporters: [prometheus]`
  - Existing `metrics`, `traces`, `logs` pipelines unchanged
  - 225 unit tests pass

---

## Milestone 1.5 — Tech Debt: ADRs, Stale Docs & Skills Sync

*Theme: Fix documentation debt created by the Loki and Grafana upgrades that happened without ADRs. Update stale references across skills, ARCHITECTURE.md, and related docs.*

**Priority: P0** — Must be done before any new features, because stale docs cause agent confusion.

### Task M1.5-01: Update ADR-001 (Loki Version) and Create ADR-004 (Grafana 12)

- **Description:** ADR-001 was stale — it said "Use Loki 2.9.10" but the actual deployment is 3.3.2. ADR-004 for Grafana 12 migration was never created.
- **Backlog Issue:** #62 (OBS-VER-04)
- **Status:** ✅ DONE
- **Tasks:**
  1. Updated `docs/adr/ADR-001-loki-version.md`:
     - Changed stated version from 2.9.10 to 3.3.2
     - Updated schema references from v11/boltdb to v13/TSDB
     - Added update date (2026-06-28) and supersession notes
     - Added migration summary referencing PR #116
  2. Created `docs/adr/ADR-004-grafana-12x-migration.md`:
     - Documented the 10.4.5 → 12.3.7 upgrade
     - Noted breaking changes assessed (Angular removal, legacy alerting, etc.)
     - Verified all provisioning config compatible with Grafana 12.x
     - Referenced current version in `compose.yaml`
  3. Updated `docs/adr/README.md` index with ADR-004 row and corrected ADR-001 entry
- **Acceptance Criteria:**
  - [x] `docs/adr/ADR-001-loki-version.md` references Loki 3.3.2
  - [x] `docs/adr/ADR-004-grafana-12x-migration.md` exists
  - [x] All ADRs pass markdownlint

### Task M1.5-02: Sync ARCHITECTURE.md with Real Versions

- **Description:** `docs/ARCHITECTURE.md` listed Loki v2.9.10 and Grafana v10.4.5 — both were wrong.
- **Backlog Issue:** N/A (tech debt discovered during audit)
- **Status:** ✅ DONE
- **Tasks:**
  1. Updated service version table: Loki → 3.3.2, Grafana → 12.3.7, Alertmanager → 0.28.0
  2. Added Prometheus rules directory to config files table
- **Acceptance Criteria:**
  - [x] `docs/ARCHITECTURE.md` version table matches `compose.yaml`
  - [x] markdownlint passes

### Task M1.5-03: Sync .agents/skills/obs-stack/SKILL.md with Real Versions

- **Description:** The obs-stack skill listed all old versions — OTel v0.103.1 (actual: 0.120.0), Prometheus v2.52.0 (actual: 2.55.1), Loki v2.9.10 (actual: 3.3.2), Tempo v2.5.0 (actual: 2.10.5), Grafana v10.4.5 (actual: 12.3.7).
- **Backlog Issue:** N/A (tech debt discovered during audit)
- **Status:** ✅ DONE
- **Tasks:**
  1. Updated service version table — all versions now match `compose.yaml`
  2. Fixed config file paths (were using old-style names like `config/otel-collector-config.yaml`)
  3. Updated OTel pipeline example to match actual `collector.yaml` contents
  4. Added Prometheus rule files table
  5. Updated port map with Tempo's additional ports (9411, 14250, 14268)
  6. Added profiles section and related skills reference
- **Acceptance Criteria:**
  - [x] `.agents/skills/obs-stack/SKILL.md` versions match `compose.yaml`
  - [x] markdownlint passes

---

## Milestone 2 — Docs, Metadata & Repository Hardening

*Theme: Establish stable development workflow, document architecture limits, and configure standard PR gates.*

**Priority: P0**

### Task M2-01: Create CONTRIBUTING.md, CODE_OF_CONDUCT.md, and Issue Templates

- **Description:** Establish community guidelines and create standardized issue templates for bugs and features.
- **Backlog Issue:** #71
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Author a comprehensive `CONTRIBUTING.md` detailing pytest instructions, pre-commit configuration, commit formats, and compose rules.
  2. Create standard issue templates in `.github/ISSUE_TEMPLATE/` for bug reports and feature requests.
  3. Formulate `CODE_OF_CONDUCT.md` following the Contributor Covenant.
- **Acceptance Criteria:**
  - `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` exist in the repo root.
  - `.github/ISSUE_TEMPLATE/bug_report.md` exists.

### Task M2-02: GitOps Standards (dependabot, FUNDING, CHANGELOG, CODEOWNERS)

- **Description:** Implement cross-repo GitOps standards as defined in issue #63.
- **Backlog Issue:** #63
- **Status:** ✅ DONE (PR #128)
- **Tasks:**
  1. Updated `.github/dependabot.yml` — added Docker ecosystem alongside existing GHA
  2. Fixed `.github/FUNDING.yml` — `github: paruff` → `github: [paruff]` (array format)
  3. Created `CHANGELOG.md` in Keep a Changelog v1.1.0 format
  4. Verified `.github/CODEOWNERS` — already exists with `* @paruff` (no change needed)
  5. Applied `v0.1.0` tag (annotated) to main HEAD, pushed
  6. Created `good-first-issue` label and applied to 5 issues (#71, #75, #84, #79, #78)
- **Acceptance Criteria:**
  - [x] `.github/dependabot.yml` exists with Docker and GHA ecosystems
  - [x] `.github/FUNDING.yml` exists with array format
  - [x] `CHANGELOG.md` exists with initial entry
  - [x] `CODEOWNERS` exists
  - [x] Tag `v0.1.0` applied
  - [x] `good-first-issue` label created and applied

### Task M2-03: Publish and Verify Platform Documentation

- **Description:** Document current platform metrics, limits, and service inter-dependencies.
- **Backlog Issue:** #74
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Author `docs/ARCHITECTURE.md` mapping OTel Collector pipelines, service ports, and container dependencies. (Architecture doc already exists but needs version sync — see M1.5-02)
  2. Document `docs/KNOWN_LIMITATIONS.md` noting storage limits, retention behaviors, and development setups.
  3. Establish `docs/CHANGE_IMPACT_MAP.md` mapping cross-service effects.
- **Acceptance Criteria:**
  - `docs/ARCHITECTURE.md`, `docs/KNOWN_LIMITATIONS.md`, and `docs/CHANGE_IMPACT_MAP.md` are present and valid markdown.

### Task M2-04: Add Repository Metadata, Topics, and CI Badge

- **Description:** Harden repo landing pages with metadata, appropriate topics, and automated workflow badges.
- **Backlog Issue:** #75
- **Dependencies:** M2-03
- **Status:** ✅ DONE (PR #130)
- **Tasks:**
  1. Verified CI badge already present in `README.md` (line 3)
  2. Fixed stale test count: 118 → 239
  3. Set GitHub homepage URL: https://ufawkes.dev
  4. Added GitHub topics: opentelemetry, docker-compose, gitops, alertmanager, tempo, loki
- **Acceptance Criteria:**
  - [x] `README.md` includes the GHA badge (verified present)
  - [x] Test count shows 239 (not 118)
  - [x] Homepage URL set to https://ufawkes.dev
  - [x] GitHub topics updated with missing technology identifiers

---

## Milestone AI — AI Observability

*Theme: Implement AI observability features enabling tracking of LLM latency, token usage, acceptance rates, and rework rate via Prometheus + Grafana.*

**Priority: P1** — Unblocks skills suite verification against running uFawkesObs.

### Task OBS-AI-01: OTel AI Metrics Pipeline

- **Description:** Add `metrics/ai` pipeline to OTel Collector with `filter/ai` and `attributes/ai` processors.
- **Backlog Issue:** #55
- **Status:** ✅ DONE (PR #123 merged)
- **Acceptance Criteria:**
  - [x] `filter/ai` processor with `error_mode: ignore` and regexp patterns for `gen_ai.*`, `llm.*`, `openllmetry.*`, `ai.*`
  - [x] `attributes/ai` processor inserts `ai.environment=development` and `ai.platform=fawkes-idp`
  - [x] `metrics/ai` pipeline wired: `receivers: [otlp]`, `processors: [memory_limiter, filter/ai, attributes/ai, batch]`, `exporters: [prometheus]`
  - [x] Existing pipelines unchanged, 225 unit tests pass

### Task OBS-AI-02: Prometheus AI Recording Rules

- **Description:** Configure recording rules for AI capabilities: token consumption rate, P95 operation latency, error rate, acceptance rate, and rework rate.
- **Backlog Issue:** #56
- **Dependencies:** OBS-AI-01 (AI pipeline deployed so metrics can flow)
- **Status:** 🔲 PENDING
- **Notes:** Use GPT-5.1-Codex per model routing table (PromQL rules require Codex to avoid `vector(0)` arithmetic errors)
- **Acceptance Criteria:**
  - [ ] `config/prometheus/rules/ufawkesobs-ai-metrics.yml` created
  - [ ] Recording rules for: token consumption rate, P95 latency, error rate, acceptance rate, rework rate
  - [ ] All rules guarded with `or vector(0)` to avoid absent() gaps
  - [ ] Prometheus reloads rules without errors

### Task OBS-AI-03: Grafana AI Capabilities Dashboard

- **Description:** Create Grafana dashboard with panels for LLM latency, token usage, acceptance rate, and rework rate with DORA 2025 performance thresholds.
- **Backlog Issue:** #57
- **Dependencies:** OBS-AI-02 (Prometheus rules provide the data)
- **Status:** 🔲 PENDING
- **Notes:** Start with Gemini 3 Flash trial for dashboard JSON (0.33x cost); fall back to GPT-5.1-Codex if revision count exceeds target
- **Acceptance Criteria:**
  - [ ] `dashboards/platform/ai-capabilities.json` created
  - [ ] Panels for latency P95, token throughput, error rate, acceptance rate, rework rate
  - [ ] DORA 2025 performance band thresholds (Elite/High/Medium/Low)
  - [ ] Datasource UIDs use string references (`prometheus`), not numeric IDs
  - [ ] Grafana provisions and renders dashboard without errors

### Task OBS-AI-04: AI Observability Documentation

- **Description:** Add AI observability setup guide and update AGENTS.md with AI pipeline documentation.
- **Backlog Issue:** #58
- **Dependencies:** OBS-AI-02, OBS-AI-03
- **Status:** ✅ DONE (PR #127)
- **Tasks:**
  1. Created `docs/ai-observability-guide.md` with architecture diagram, metrics/alert/dashboard reference, instrumentation guide, and DORA 2025 thresholds
  2. Updated `AGENTS.md` — fixed version table (Loki 3.3.2, Grafana 12.3.7), added AI guide to context files
  3. Updated `.agents/skills/otel-collector/SKILL.md` — synced pipeline map and AI pipeline to actual config
  4. Updated `docs/CHANGE_IMPACT_MAP.md` — added dashboards section, AI entries
- **Acceptance Criteria:**
  - [x] `docs/ai-observability-guide.md` created with AI observability overview
  - [x] `AGENTS.md` updated with AI pipeline and rule references
  - [x] Skills files updated if needed

---

## Milestone 3 — Cross-Plane Integration Guides

*Theme: Provide guides enabling other planes (e.g. uFawkesPipe, uFawkesDevX) to join the observability subnet.*

**Priority: P1**

### Task M3-01: Add uFawkesPipe Telemetry Integration Guide

- **Description:** Guide developer teams on how to stream pipeline lifecycle tracing to uFawkesObs Tempo.
- **Backlog Issue:** #76
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Author `docs/examples/uFawkesPipe-integration.md`.
  2. Provide clear examples of export headers, OTLP endpoint parameters (`otel-collector:4317`), and trace visualization procedures in Grafana.
- **Acceptance Criteria:**
  - `docs/examples/uFawkesPipe-integration.md` exists.

### Task M3-02: Add uFawkesDevX Developer Telemetry Integration Guide

- **Description:** Provide examples for developers to integrate application metrics/spans into the central OTel collector.
- **Backlog Issue:** #77
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Author `docs/examples/uFawkesDevX-integration.md`.
  2. Provide code snippets (Python/Node/Go) explaining standard OpenTelemetry SDK setup pointing to uFawkesObs.
- **Acceptance Criteria:**
  - `docs/examples/uFawkesDevX-integration.md` exists.

### Task M3-03: Register uFawkesObs in Backstage Catalog

- **Description:** Add uFawkesObs metadata in the central Backstage platform catalog.
- **Backlog Issue:** #78
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Verify and populate `catalog-info.yaml` with service owner, system plane, lifecycle, and component taxonomy details.
- **Acceptance Criteria:**
  - `catalog-info.yaml` parses correctly and conforms to Backstage schema models.

### Task M3-04: Update Multi-Stack Integration Guide

- **Description:** Document compose project joining patterns to connect developer services to the local observability network.
- **Backlog Issue:** #79
- **Dependencies:** M3-01, M3-02
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Update `docs/multi-stack-integration.md` with explicit details on how external compose networks join the `observability-lab` bridge.
- **Acceptance Criteria:**
  - `docs/multi-stack-integration.md` contains networking section with `external: true` example.

### Task M3-05: Create docker-compose.integration.yml and Multi-Stack Network Join Docs

- **Description:** Document how uFawkesObs connects to uFawkesDORA, uFawkesPipe, and uFawkesSec over a shared Docker network. Create the compose-them-all file.
- **Backlog Issue:** #54 (OBS-DORA-05)
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Create `docs/MULTI_STACK_INTEGRATION.md` with sections for each sister stack
  2. Create `docker-compose.integration.yml` at repo root
  3. Add `make integration-up` and `make integration-down` targets
- **Acceptance Criteria:**
  - [ ] `docs/MULTI_STACK_INTEGRATION.md` exists with architecture diagram, step-by-step network join, and troubleshooting
  - [ ] `docker-compose.integration.yml` wires all active stacks via shared `ufawkes-net` external network
  - [ ] Makefile targets exist
  - [ ] README updated

---

## Milestone 4 — DORA Metrics & DevLake Integration

*Theme: Formulate the DORA metrics contract, provision Apache DevLake, and render dashboards.*

**Priority: P1**

### Task M4-01: Define DORA Data Contract

- **Description:** Define what counts as a deployment, incident, and restoration within uFawkesObs telemetry.
- **Backlog Issue:** #80
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Create `docs/adr/ADR-004-dora-metric-definitions.md` detailing metric mappings and semantics.
- **Acceptance Criteria:**
  - ADR-004 exists and is linked from docs.

### Task M4-02: Add DevLake + MySQL to Compose Stack under DORA Profile

- **Description:** Integrate Apache DevLake database and worker instances into the docker-compose orchestration.
- **Backlog Issue:** #81, #51
- **Dependencies:** M4-01
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Define `devlake` and `mysql` services inside `compose.yaml` under the `dora` profile.
  2. Pin exact semantic images and define volume paths for persistent storage.
  3. Define custom healthchecks for DevLake.
- **Acceptance Criteria:**
  - `docker compose --profile dora config` succeeds with zero parsing warnings.

### Task M4-03: Add DORA Recording Rules to Prometheus

- **Description:** Configure Prometheus recording rules inside uFawkesObs for continuous calculation of DORA metrics.
- **Backlog Issue:** #82, #53
- **Dependencies:** M4-02
- **Status:** 🔲 PENDING
- **Notes:** Use GPT-5.1-Codex per model routing table (PromQL rules)
- **Tasks:**
  1. Formulate recording rules for `dora:deployment_frequency:rate30d`, `dora:lead_time_hours:p50_30d`, `dora:change_failure_rate:ratio30d`, and `dora:mttr_hours:p50_30d` inside dedicated rule file.
- **Acceptance Criteria:**
  - Prometheus rules load and parse cleanly.
  - All rules guarded with `or vector(0)`.

### Task M4-04: Provision Grafana DORA Metrics Dashboard

- **Description:** Pre-provision a dedicated DORA dashboard in Grafana showing real-time calculations.
- **Backlog Issue:** #83, #52
- **Dependencies:** M4-03
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Create `config/grafana/dashboards/dora-metrics.json` containing panel models for the 4 DORA indicators.
  2. Enforce standard DORA performance bands (Elite/High/Medium/Low) using color thresholds.
- **Acceptance Criteria:**
  - Dashboard JSON exists and is mapped inside `config/grafana/provisioning/dashboards/`.
  - Datasource UIDs use string references (`prometheus`), not numeric IDs.

---

## Milestone 5 — Kubernetes & Helm Deployment Strategy

*Theme: Scale the observability substrate from Docker Compose to cloud-native Kubernetes environments.*

**Priority: P2** — Far-term; no immediate dependency.

### Task M5-01: Document Kubernetes Deployment Strategy

- **Description:** Author an ADR specifying the K8s migration path and architectural requirements.
- **Backlog Issue:** #84
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Create `docs/adr/ADR-005-kubernetes-migration.md`.
- **Acceptance Criteria:**
  - ADR-005 exists.

### Task M5-02: Create Helm Chart for uFawkesObs Core Stack

- **Description:** Create an umbrella Helm chart to deploy OTel, Prometheus, Loki, Tempo, Alloy, and Grafana.
- **Backlog Issue:** #85
- **Dependencies:** M5-01
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Scaffold umbrella chart in `helm/ufawkes-obs/`.
  2. Compile core observability dependencies as pinned Helm sub-charts.
- **Acceptance Criteria:**
  - `helm lint helm/ufawkes-obs/` passes with 0 warnings.

### Task M5-03: Create k3d Local Simulator and Makefile Targets

- **Description:** Add Makefile helpers to quickly spin up a local cluster and deploy uFawkesObs.
- **Backlog Issue:** #86
- **Dependencies:** M5-02
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Add `make k3d-up`, `make k3d-down`, and `make helm-deploy` targets.
- **Acceptance Criteria:**
  - Running `make k3d-up` correctly boots k3d and deploys the Helm chart.

### Task M5-04: Create Kubernetes Acceptance Testing Workflow

- **Description:** Configure GitHub Actions workflows to verify Helm installations in a simulated cluster.
- **Backlog Issue:** #87
- **Dependencies:** M5-03
- **Status:** 🔲 PENDING
- **Tasks:**
  1. Configure GHA pipeline to boot a KinD/k3d cluster, install the Helm chart, and run verification probes.
- **Acceptance Criteria:**
  - GitHub Action parses cleanly and tests pass.
