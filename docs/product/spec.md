# uFawkesObs — Specification

**Version:** 1.0.0
**Date:** 2026-06-28
**Repo:** paruff/uFawkesObs
**Plane:** Observability
**Status:** Approved

---

## 1. Purpose

uFawkesObs is the self-hosted, GitOps-first **Observability Plane** for the entire uFawkes suite. It delivers a consolidated telemetry substrate (metrics, logs, traces, and alert routing) to all developer and delivery tools within the ecosystem.

Rather than having each repository or plane provision its own isolated, custom telemetry stack, all uFawkes components instruments into and integrates with uFawkesObs. It provides unified ingestion endpoints and a single pane of glass for visualization.

---

## 2. Scope Boundaries

### In Scope

- **Metrics Collection & Storage:** Prometheus scrapes metrics from target hosts, exporter processes, and OTel endpoints.
- **Log Aggregation:** Loki aggregates system and container-level logs shipped via Alloy.
- **Trace Aggregation:** Tempo provides highly scalable distributed trace storage for OTLP spans.
- **Unified Telemetry Ingestion:** OpenTelemetry Collector processes and routes OTLP metric, log, and trace streams.
- **Container Log Discovery:** Grafana Alloy discovers and streams Docker container stdout/stderr log pipelines.
- **Alert Ingestion & Routing:** Alertmanager handles alert deduplication and notification dispatch.
- **Visualization & Provisioning:** Grafana pre-provisions dashboards, datasource definitions, and permissions.
- **GitOps Reconciliation:** Auto-reconciliation of runtime configurations and stack deployment via SSH-triggered workflows.

### Out of Scope — Forever

- **CI/CD Orchestration:** uFawkesPipe owns all integration pipelines and workflow execution.
- **Secret Management Substrate:** Vault/uFawkesSec manages root credentials and rotation. uFawkesObs only consumes secrets via `.env` injection.
- **Platform Engineering CLI & Portal:** The centralized developer interface and portal (fawkes) embeds or queries uFawkesObs but does not replace it.

---

## 3. Versioned Milestones

| Milestone | Theme | Scope | Status |
|---|---|---|---|
| **M1 (v1.0.0)** | Substrate Core | Core Docker Compose stack (OTel Collector, Prometheus, Alertmanager, Tempo, Loki, Alloy, Grafana) with automated local unit/integration test gates. | **Completed** |
| **M2 (v1.1.0)** | Repo Hardening | Standardized CONTRIBUTING rules, issue templates, ARCHITECTURE mapping, KNOWN_LIMITATIONS documentation, and repo badges. | **Backlog** (M2-01 to M2-05) |
| **M3 (v1.2.0)** | Cross-Plane Docs | Structured guides for joining uFawkesPipe, uFawkesDevX, and Backstage catalog registration. | **Backlog** (M3-01 to M3-04) |
| **M4 (v1.3.0)** | DORA & Ecosystem | Wire uFawkesObs to uFawkesDORA compute plane and uFawkesRes shared PostgreSQL, implement Prometheus DORA recording rules, and provision Grafana DORA dashboards. | **Backlog** (M4-01 to M4-04) |
| **M5 (v2.0.0)** | Kubernetes Deploy | Kubernetes deployment ADR, Helm charts for the core stack, k3d local simulator, and k8s-based acceptance pipelines. | **Backlog** (M5-01 to M5-04) |

---

## 4. Functional Requirements

### 4.1 M1 (v1.0.0) — Core Observability Substrate

- **OBS-F01:** Expose an OpenTelemetry Collector OTLP endpoint (gRPC 4317 / HTTP 4318) for incoming trace, metric, and log streams.
- **OBS-F02:** Automatically scrape container logs via Grafana Alloy using Docker socket monitoring and forward them structured to Loki.
- **OBS-F03:** Scrape system/hardware metrics from target hosts via Prometheus Node Exporter.
- **OBS-F04:** Provide pre-provisioned, declarative datasources in Grafana pointing to Prometheus, Loki, Tempo, and Alertmanager.
- **OBS-F05:** Pre-load system performance dashboards for host system, container logs, and telemetry flow metrics.
- **OBS-F06:** Run automated health checking of all stack services via Docker Compose healthchecks and local test automation.

### 4.2 Backlog — Repository Hardening & Cross-Plane (M2 & M3)

- **OBS-F10:** Document the precise network join patterns in `multi-stack-integration.md` to allow other planes (e.g., developerd, deliveryd) to join the `observability-lab` Docker bridge network.
- **OBS-F11:** Register uFawkesObs into fawkes Backstage catalog-info.yaml metadata.
- **OBS-F12:** Provide clear guide explaining how uFawkesPipe CI pipelines can export OTLP tracing to uFawkesObs Tempo.

### 4.3 Backlog — DORA & Ecosystem Integration (M4)

- **OBS-F20:** Define the DORA data contract mapping of what counts as a deployment, incident, and lead-time event inside uFawkesObs telemetry. This contract is consumed by uFawkesDORA's ingestion API.
- **OBS-F21:** Implement Prometheus recording rules inside `config/prometheus/rules/` computing Deployment Frequency, Lead Time for Changes, Change Failure Rate, and Failed Deployment Recovery Time (FDRT).
- **OBS-F22:** Pre-provision a "DORA Metrics" Grafana dashboard showing historical stat panels and trendlines for all 4 DORA indicators. Dashboard reads from Prometheus (time-series) and uFawkesRes PostgreSQL (current snapshots via Postgres datasource plugin).
- **OBS-F23:** Configure uFawkesObs to connect to uFawkesRes's shared PostgreSQL on `fawkes-backbone-net` for DORA metric snapshots, and to uFawkesDORA's ingestion API for event forwarding.

**Out of scope for M4 (moved to uFawkesDORA/uFawkesRes):**
- Apache DevLake — now owned by uFawkesDORA as optional complementary visualization
- MySQL database — DevLake uses uFawkesRes's shared PostgreSQL instead

### 4.4 Backlog — Kubernetes & Helm Deployment (M5)

- **OBS-F30:** Formulate an Architecture Decision Record (ADR-004) specifying the migration path from Docker Compose orchestration to native Kubernetes resources.
- **OBS-F31:** Author a Helm umbrella chart (`helm/ufawkes-obs`) compiling Prometheus, Loki, Tempo, Grafana, Alloy, and OTel Collector as standard sub-charts.
- **OBS-F32:** Provide a local k3d Kubernetes bootstrap script/Makefile command to run acceptance verification in-cluster.

---

## 5. Non-Functional Requirements

- **OBS-N01 (Unit Tests):** Maintain a suite of unit test validators verifying configuration files (yaml parser syntax, correct ports, required sections) for Loki, Prometheus, OTel, and Grafana.
- **OBS-N02 (Integration Tests):** Require integration test cases that run containerized against active compose services to verify end-to-end trace queries, log searches, and scrape targets.
- **OBS-N03 (Scrape Frequency):** Default scrape interval set to `30s` for standard workloads, minimizing resource overhead while providing high resolution.
- **OBS-N04 (Zero Secret Commits):** Absolutely zero credentials, API keys, or database passwords in source files or configuration manifests. Enforce via Gitleaks and Yelp detect-secrets pre-commit hooks.
- **OBS-N05 (Pinned Versions):** All third-party images defined in `compose.yaml` must be explicitly pinned to precise semantic versions (no `latest` or floating tag versions allowed).

---

## 6. Interface Contracts

| Interface | Direction | Protocol / Port | Purpose | Consumer |
|---|---|---|---|---|
| **OTLP Ingestion** | Inbound | gRPC 4317 / HTTP 4318 | Standardized telemetry stream ingestion (Metrics, Logs, Traces) | uFawkesPipe, uFawkesDevX, and custom apps |
| **Log Collection** | Pull | Docker API Socket | Harvest host container logs via Alloy daemon | Local Docker Engine |
| **Scrape Targets** | Pull | HTTP `/metrics` | Prometheus pulls performance indicators | OTel Collector, Alloy, Node Exporter, custom apps |
| **Alert manager API** | Inbound | HTTP 9093 | Prometheus fires alerts on breach of rules | Prometheus, custom alerting proxies |
| **Query Engine APIs** | Inbound | HTTP `/api/v1` | External services query Prometheus/Loki/Tempo databases | Grafana, uFawkesAI/measure, uFawkesDORA |
| **Visualization portal** | Inbound | HTTP 3000 | Developer and platform monitoring dashboard | Platform engineers, developers |

---

## 7. Confirmed Stack

| Component | Version | Role | Mount / Vol Data | Configuration File |
|---|---|---|---|---|
| **OpenTelemetry Collector** | `0.120.0` | Telemetry processing and fanout | None | `config/otel/collector.yaml` |
| **Prometheus** | `v2.55.1` | Metrics TSDB & scrape engine | `./data/prometheus` | `config/prometheus/prometheus.yaml` |
| **Alertmanager** | `v0.27.0` | Notification aggregator & router | `./data/alertmanager` | `config/alertmanager/alertmanager.yml` |
| **Tempo** | `2.10.5` | Distributed trace database | `./data/tempo` | `config/tempo/tempo.yaml` |
| **Loki** | `2.9.10` | Log indexer & backend | `./data/loki` | `config/loki/loki.yaml` |
| **Alloy** | `v1.12.2` | Container log discovery & forwarding | `./data/alloy` | `config/alloy/config.river` |
| **Grafana** | `10.4.5` | Metrics, logs, & trace dashboard UI | `./data/grafana` | `config/grafana/grafana.ini` |
| **Node Exporter** | `v1.8.1` | Host system exporter | Host read mounts | None |
