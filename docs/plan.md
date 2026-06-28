# uFawkesObs — Implementation Plan

**Version:** 1.0.0
**Date:** 2026-06-28
**Repo:** paruff/uFawkesObs
**Status:** Active

---

## Guide to Using This Plan

- This implementation plan guides the development of the uFawkesObs platform.
- Tasks are derived from the actual open issues backlog in `gh issue list`.
- Do not start any task until all its **Dependencies** are fully completed.
- Every task must be verified with automated test gates (such as `make test`) before being marked complete.

---

## Milestone 2 — Docs, Metadata & Repository Hardening

*Theme: Establish stable development workflow, document architecture limits, and configure standard PR gates.*

### Task M2-01: Create CONTRIBUTING.md, CODE_OF_CONDUCT.md, and Issue Templates

- **Description:** Establish community guidelines and create standardized issue templates for bugs and features.
- **Backlog Issue:** #71
- **Tasks:**
  1. Author a comprehensive `CONTRIBUTING.md` detailing pytest instructions, pre-commit configuration, commit formats, and compose rules. (Already complete)
  2. Create standard issue templates in `.github/ISSUE_TEMPLATE/` for bug reports and feature requests.
  3. Formulate `CODE_OF_CONDUCT.md` following the Contributor Covenant.
- **Acceptance Criteria:**
  - `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` exist in the repo root.
  - `.github/ISSUE_TEMPLATE/bug_report.md` exists.

### Task M2-04: Publish and Verify Platform Documentation

- **Description:** Document current platform metrics, limits, and service inter-dependencies.
- **Backlog Issue:** #74
- **Tasks:**
  1. Author `docs/ARCHITECTURE.md` mapping OTel Collector pipelines, service ports, and container dependencies. (Already complete)
  2. Document `docs/KNOWN_LIMITATIONS.md` noting storage limits, retention behaviors, and development setups.
  3. Establish `docs/CHANGE_IMPACT_MAP.md` mapping cross-service effects.
- **Acceptance Criteria:**
  - `docs/ARCHITECTURE.md`, `docs/KNOWN_LIMITATIONS.md`, and `docs/CHANGE_IMPACT_MAP.md` are present and valid markdown.

### Task M2-05: Add Repository Metadata, Topics, and CI Badge

- **Description:** Harden repo landing pages with metadata, appropriate topics, and automated workflow badges.
- **Backlog Issue:** #75
- **Dependencies:** M2-04
- **Tasks:**
  1. Add a live GitHub Actions CI pipeline passing status badge to `README.md`.
  2. Update repo description, landing page URLs, and tags (such as `opentelemetry`, `prometheus`, `grafana`, `docker-compose`, `gitops`).
- **Acceptance Criteria:**
  - `README.md` includes the GHA badge.
  - GitHub topics updated.

---

## Milestone 3 — Cross-Plane Integration Guides

*Theme: Provide guides enabling other planes (e.g. uFawkesPipe, uFawkesDevX) to join the observability subnet.*

### Task M3-01: Add uFawkesPipe Telemetry Integration Guide

- **Description:** Guide developer teams on how to stream pipeline lifecycle tracing to uFawkesObs Tempo.
- **Backlog Issue:** #76
- **Tasks:**
  1. Author `docs/examples/uFawkesPipe-integration.md`.
  2. Provide clear examples of export headers, OTLP endpoint parameters (`otel-collector:4317`), and trace visualization procedures in Grafana.
- **Acceptance Criteria:**
  - `docs/examples/uFawkesPipe-integration.md` exists.

### Task M3-02: Add uFawkesDevX Developer Telemetry Integration Guide

- **Description:** Provide examples for developers to integrate application metrics/spans into the central OTel collector.
- **Backlog Issue:** #77
- **Tasks:**
  1. Author `docs/examples/uFawkesDevX-integration.md`.
  2. Provide code snippets (Python/Node/Go) explaining standard OpenTelemetry SDK setup pointing to uFawkesObs.
- **Acceptance Criteria:**
  - `docs/examples/uFawkesDevX-integration.md` exists.

### Task M3-03: Register uFawkesObs in Backstage Catalog

- **Description:** Add uFawkesObs metadata in the central Backstage platform catalog.
- **Backlog Issue:** #78
- **Tasks:**
  1. Verify and populate `catalog-info.yaml` with service owner, system plane, lifecycle, and component taxonomy details.
- **Acceptance Criteria:**
  - `catalog-info.yaml` parses correctly and conforms to Backstage schema models.

### Task M3-04: Update Multi-Stack Integration Guide

- **Description:** Document compose project joining patterns to connect developer services to the local observability network.
- **Backlog Issue:** #79
- **Dependencies:** M3-01, M3-02
- **Tasks:**
  1. Update `docs/multi-stack-integration.md` with explicit details on how external compose networks join the `observability-lab` bridge.
- **Acceptance Criteria:**
  - `docs/multi-stack-integration.md` contains networking section with `external: true` example.

---

## Milestone 4 — DORA Metrics & DevLake Integration

*Theme: Formulate the DORA metrics contract, provision Apache DevLake, and render dashboards.*

### Task M4-01: Define DORA Data Contract

- **Description:** Define what counts as a deployment, incident, and restoration within uFawkesObs telemetry.
- **Backlog Issue:** #80
- **Tasks:**
  1. Create `docs/adr/ADR-004-dora-metric-definitions.md` detailing metric mappings and semantics.
- **Acceptance Criteria:**
  - ADR-004 exists and is linked from docs.

### Task M4-02: Add DevLake + MySQL to Compose Stack under DORA Profile

- **Description:** Integrate Apache DevLake database and worker instances into the docker-compose orchestration.
- **Backlog Issue:** #81, #51
- **Dependencies:** M4-01
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
- **Tasks:**
  1. Formulate recording rules for `dora:deployment_frequency:rate30d`, `dora:lead_time_hours:p50_30d`, `dora:change_failure_rate:ratio30d`, and `dora:mttr_hours:p50_30d` inside `config/prometheus/alerts.yml` (or dedicated recording rule file).
- **Acceptance Criteria:**
  - Prometheus rules load and parse cleanly.

### Task M4-04: Provision Grafana DORA Metrics Dashboard

- **Description:** Pre-provision a dedicated DORA dashboard in Grafana showing real-time calculations.
- **Backlog Issue:** #83, #52
- **Dependencies:** M4-03
- **Tasks:**
  1. Create `config/grafana/dashboards/dora-metrics.json` containing panel models for the 4 DORA indicators.
  2. Enforce standard DORA performance bands (Elite/High/Medium/Low) using color thresholds.
- **Acceptance Criteria:**
  - Dashboard JSON exists and is mapped inside `config/grafana/provisioning/dashboards/`.

---

## Milestone 5 — Kubernetes & Helm Deployment Strategy

*Theme: Scale the observability substrate from Docker Compose to cloud-native Kubernetes environments.*

### Task M5-01: Document Kubernetes Deployment Strategy

- **Description:** Author an ADR specifying the K8s migration path and architectural requirements.
- **Backlog Issue:** #84
- **Tasks:**
  1. Create `docs/adr/ADR-005-kubernetes-migration.md`.
- **Acceptance Criteria:**
  - ADR-005 exists.

### Task M5-02: Create Helm Chart for uFawkesObs Core Stack

- **Description:** Create an umbrella Helm chart to deploy OTel, Prometheus, Loki, Tempo, Alloy, and Grafana.
- **Backlog Issue:** #85
- **Dependencies:** M5-01
- **Tasks:**
  1. Scaffold umbrella chart in `helm/ufawkes-obs/`.
  2. Compile core observability dependencies as pinned Helm sub-charts.
- **Acceptance Criteria:**
  - `helm lint helm/ufawkes-obs/` passes with 0 warnings.

### Task M5-03: Create k3d Local Simulator and Makefile Targets

- **Description:** Add Makefile helpers to quickly spin up a local cluster and deploy uFawkesObs.
- **Backlog Issue:** #86
- **Dependencies:** M5-02
- **Tasks:**
  1. Add `make k3d-up`, `make k3d-down`, and `make helm-deploy` targets.
- **Acceptance Criteria:**
  - Running `make k3d-up` correctly boots k3d and deploys the Helm chart.

### Task M5-04: Create Kubernetes Acceptance Testing Workflow

- **Description:** Configure GitHub Actions workflows to verify Helm installations in a simulated cluster.
- **Backlog Issue:** #87
- **Dependencies:** M5-03
- **Tasks:**
  1. Configure GHA pipeline to boot a KinD/k3d cluster, install the Helm chart, and run verification probes.
- **Acceptance Criteria:**
  - GitHub Action parses cleanly and tests pass.
