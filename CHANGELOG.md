# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `good-first-issue` label and GitHub metadata standards (M2-02)
- `.github/dependabot.yml` Docker ecosystem for `compose.yaml` image scanning
- **CONTRIBUTING.md, CODE_OF_CONDUCT.md, GitHub issue templates** (M2-01, issue #71)
- **Cross-plane integration guides** (Milestone 3): uFawkesPipe and uFawkesDevX
  telemetry integration guides, Backstage catalog registration
  (`catalog-info.yaml`), expanded multi-stack integration guide with
  Kubernetes integration section and minimal-startup patterns, and
  `docker-compose.integration.yml` for joining sister-plane stacks
  (issues #76-79, #54; PR #131, #133, #134, #135, #136, #138)
- **DORA metrics & ecosystem integration** (Milestone 4): `docs/adr/ADR-006-dora-metric-definitions.md`
  data contract, `dora` compose profile wiring `otel-collector-dora` to
  uFawkesDORA's ingestion API and uFawkesRes's shared PostgreSQL, 5 Prometheus
  DORA recording rules (deployment frequency, lead time, change failure rate,
  FDRT, and DORA-2026's 5th metric — rework rate) with paired alert rules, and
  a provisioned Grafana DORA metrics dashboard (issues #80-83, #51-53; PR #147,
  #148, #154, #149/#155)
- **Acceptance test suite**: BDD-style acceptance tests across 7 phases (SLOs,
  synthetic workload generators, chaos/failure-injection scenarios, evidence
  capture, CI integration) plus a nightly chaos test workflow
  (`.github/workflows/ci-chaos-nightly.yml`)
- **GitOps lifecycle gates**: post-deployment verification and automatic
  rollback on failed smoke tests (PR #166)
- `AGENTS.md` template guidance for reuse across repos (PR #150)
- `docs/product/` and `docs/features/` directories separating product-level
  discovery/spec/design docs from per-feature pipeline output (repo hygiene)

### Changed

- `.github/FUNDING.yml` syntax to GitHub array format
- **Prometheus upgraded** from v2.55.1 → v3.5.4 (PR #136)
- DORA scope narrowed per `docs/reviews/M4-02-ecosystem-review.md`: DevLake +
  MySQL moved to uFawkesDORA's own stack; uFawkesObs's DORA responsibility is
  now limited to the data contract, recording rules, and dashboard
- `compose.yaml`'s `otel-collector-dora.DORA_POSTGRES_URL` no longer has a
  hardcoded credential fallback — now a required `.env` value, documented in
  `.env.example`

### Fixed

- Stale `media-refinery` app references in `docs/OBSERVABILITY_STATUS.md`
  corrected to `telemetry-generator` (the actual demo app)
- Reconciled `docs/plan.md` status column against real GitHub issue state
  (multiple tasks were done but still shown pending)

## [0.1.0] — 2026-06-28

### Added

- **Initial observability stack:** Docker Compose with OpenTelemetry Collector v0.120.0,
  Prometheus v2.55.1, Alertmanager v0.28.0, Tempo v2.10.5, Loki v3.3.2, Alloy v1.12.2,
  and Grafana v12.3.7
- **OTel AI metrics pipeline:** `metrics/ai` pipeline with `filter/ai` + `attributes/ai`
  processors for LLM telemetry routing (issue #55)
- **Prometheus AI recording rules:** `ai:llm_token_rate:rate5m`,
  `ai:suggestion_latency:percentile99`, `ai:suggestion_acceptance_rate:ratio`,
  `ai:rework_rate:ratio` — all guarded with `or vector(0)` (issue #56)
- **Prometheus AI alert rules:** 8 alerts covering P99 latency spikes, acceptance drops,
  rework rate increases, token rate anomalies, and composite capability degradation —
  grouped by DORA 2025 performance bands
- **Grafana AI capabilities dashboard:** 9-panel dashboard with DORA 2025 thresholds —
  latency P99/P50, token rate, acceptance rate, rework rate, and alertlist (issue #57)
- **AI observability documentation:** `docs/ai-observability-guide.md` with architecture
  diagram, metrics/alert/dashboard reference, and instrumentation guide (issue #58)
- **AI runbook:** `docs/ai-runbook.md` with step-by-step remediation for all 8 alerts (issue #56)
- **ADR-001:** Loki version upgrade decision (v2.9.10 → v3.3.2)
- **ADR-004:** Grafana 12.x migration decision (v10.4.5 → v12.3.7)
- **Unit tests:** schema version guards and static assertion tests
- **CI/CD pipeline:** Phase 1 (lint, validate-config, smoke, test, security) and Phase 2
  (reusable workflows via uFawkesPipe@v1.1.0, supply chain, coverage thresholds)
- **Repository skeleton:** `.github/` templates (issue templates, PR template, Copilot
  instructions), `.gitignore`, Makefile with common commands
- **Scripts:** `start.sh`, `stop.sh`, `healthcheck.sh`, `smoke-test.sh`, `pr-create.sh`,
  Makefile pr shortcut
- **Docs:** ARCHITECTURE.md, CHANGE_IMPACT_MAP.md, KNOWN_LIMITATIONS.md, AGENTS.md,
  ADR README, multi-stack-integration.md

### Changed

- **Loki upgraded** from v2.9.10 → v3.3.2 with config migration for schema v13 and
  removed legacy `boltdb_shipper` (PR #116)
- **Grafana upgraded** from v10.4.5 → v12.3.7 with dashboard JSON migration to
  `schemaVersion: 40` and `uid`-based datasource references (PR #115)
- **Alertmanager upgraded** from v0.27.0 → v0.28.0 for CVE fixes (PR #114)
- **Tempo upgraded** from v2.5.0 → v2.10.5 (PR #100)
- **README version table** synced to match `compose.yaml` (PR #117)
- **CI consolidated** from 10 workflows to 4 (PR #106)
- **Reusable workflows** migrated to uFawkesPipe@v1.1.0 (PR #121)
- **Pre-release cleanup:** naming, docs, compose labels (PR #113)
- **ADRs, ARCHITECTURE.md, obs-stack skill** synced to match `compose.yaml` versions (PR #125)
- **AGENTS.md, OTel collector skill, CHANGE_IMPACT_MAP.md** updated with AI observability
  documentation (PR #127)

### Fixed

- `ai-rules.yml` path — moved to `config/prometheus/rules/` to match Docker volume mount
  (PR #124)
- CI main failures: Trivy action version, Gitleaks v3 migration, dependency review
  (PR #110)
- Pre-commit hook failures: trailing whitespace, markdownlint (PR #106)
- Shellcheck SC2001 warnings in scripts (PR #112)

### Dependencies

- Bumped `actions/cache` 5→6, `actions/checkout` 4→6/6→7, `actions/setup-python` 5→6,
  `actions/upload-artifact` 4→7, `actions/github-script` 7→9, `webfactory/ssh-agent`
  0.9.0→0.10.0, `aquasecurity/trivy-action` 0.35.0→0.36.0, `dorny/paths-filter` 3→4,
  `actions/dependency-review-action` 4→5

[Unreleased]: https://github.com/paruff/uFawkesObs/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/paruff/uFawkesObs/releases/tag/v0.1.0
