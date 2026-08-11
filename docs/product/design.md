# uFawkesObs — Design

**Version:** 1.1.0
**Date:** 2026-07-27
**Depends on:** docs/product/spec.md v1.1.0
**Repo:** paruff/uFawkesObs

---

## 1. Architectural Principles

uFawkesObs is built upon five design tenets:

1. **Composition Over Compilations:** Service definitions, volumes, networks, and environment bindings are orchestrated via a centralized, decoupled `compose.yaml` file using explicit profiles (`core` and `apps`).
2. **GitOps Reconciliation:** Changes made to `config/**`, `compose.yaml`, `.env.example`, and `dashboards/**` are auto-reconciled on target environments by GHA-triggered workflows over SSH.
3. **Hot Configuration Reloading:** Config-only updates use native runtime signaling (such as Prometheus HTTP POST `/-/reload` or Alloy `SIGHUP`) to prevent container downtime.
4. **Self-Monitoring:** Every telemetry service in the plane exposes a `/metrics` target scraped by Prometheus, ensuring the observability substrate is itself observable.
5. **Reproducible Local Simulation:** All integration and unit tests are designed to run fully locally without external infrastructure or cluster dependencies.

---

## 2. Repository Structure

The actual file layout is structured as follows:

```
uFawkesObs/
├── compose.yaml                      # Service definitions, volumes, and networks
├── .env.example                      # Reference template for localized configurations
├── config/                           # Declarative configurations per service
│   ├── alertmanager/
│   │   └── alertmanager.yml          # Alert routing, deduplication, and receivers
│   ├── alloy/
│   │   └── config.river              # River DSL configuration for log tailing
│   ├── grafana/
│   │   ├── grafana.ini               # Security, authentication, and database settings
│   │   └── provisioning/             # Pre-configured dashboards and datasources
│   │       ├── dashboards/
│   │       └── datasources/
│   ├── loki/
│   │   └── loki.yaml                 # Index, schema, and retention rules
│   ├── otel/
│   │   ├── collector.yaml            # Core ingestion pipeline (metrics, traces, logs)
│   │   └── collector-dora.yaml       # DORA-profile collector, forwards to uFawkesDORA ingestion
│   ├── prometheus/
│   │   ├── alerts.yml                # Alert thresholds
│   │   ├── prometheus.yaml           # Global configuration and scrapers
│   │   └── rules/                    # Recording/alerting rules (AI capability, DORA, self-monitoring)
│   └── tempo/
│       └── tempo.yaml                # Trace ingestion ports and storage configs
├── dashboards/                       # Provisioned dashboard JSON configurations
│   └── platform/                     # DORA, AI-capability, and per-component health dashboards
├── data/                             # Host directory mounts for persistent volumes (gitignored)
├── apps/
│   └── telemetry-generator/          # Demo application mimicking standard OTLP workloads
├── scripts/                          # Administration helpers and health verification tools
├── tests/
│   ├── unit/                         # Local config syntax, version, and model validators
│   ├── integration/                  # Active container test cases (Prometheus, Grafana, Loki, Tempo)
│   └── acceptance/                   # In-pipeline E2E observability checks, incl. chaos_report.py
│       ├── features/                 # Gherkin features (e.g. chaos_resilience.feature)
│       └── steps/                    # Step implementations (e.g. chaos_steps.py)
├── reports/
│   └── chaos-evidence/               # Generated evidence artifacts from chaos test runs
├── docs/
│   ├── product/                      # Whole-repo product artifacts: discovery-draft.md, spec.md,
│   │                                 #   design.md, tasks.json (this document lives here)
│   └── features/                     # Per-feature discovery/spec/design/tasks, kept after ship
│       └── chaos-failure-injection/  # Example: chaos/failure-injection feature's pipeline output
└── .github/
    └── workflows/
        ├── ci-pipeline.yml           # Unified pipeline running preflight, lint, security, build, tests
        ├── ci-acceptance-smoke.yml   # Fast acceptance gate on PRs
        ├── ci-acceptance-full.yml    # Full acceptance suite
        ├── ci-chaos-nightly.yml      # Scheduled chaos/failure-injection gate
        ├── main-ci-guard.yml         # Branch-protection guard for main
        └── deploy.yml                # GitOps reconciliation (SSH-triggered) to target environments
```

---

## 3. Component Topology

All services are orchestrated on a dedicated bridge network named `observability` (mapped externally to `observability-lab`).

```
                              ┌──────────────────────────────────┐
                              │     Telemetry Generator App      │
                              │       (OTLP gRPC Client)         │
                              └────────────────┬─────────────────┘
                                               │ OTLP / gRPC
                                               ▼
┌─────────────────────────── observability Network ──────────────────────────┐
│                                                                            │
│  ┌───────────────────────┐             ┌────────────────────────────────┐  │
│  │   Docker Engine logs  │             │     OpenTelemetry Collector    │  │
│  └──────────┬────────────┘             │            (Port 4317)         │  │
│             │ container logs           └─┬──────────────┬─────────────┬─┘  │
│             ▼                            │ OTLP/metrics │ OTLP/traces │    │
│  ┌───────────────────────┐               │              │             │    │
│  │     Grafana Alloy     │               ▼              ▼             ▼    │
│  │     (Port 12345)      │         ┌───────────┐  ┌───────────┐ ┌────────┐ │
│  └──────────┬────────────┘         │Prometheus │  │   Tempo   │ │  Loki  │ │
│             │ loki push            │ (Port 9090│  │ (Port 3200│ │(Port   │ │
│             └─────────────────────▶│   / 8889) │  │  / 9095)  │ │  3100) │ │
│                                    └─────┬─────┘  └─────┬─────┘ └────┬───┘ │
│                                          │              │            │     │
│                                          ▼              ▼            ▼     │
│                                    ┌─────────────────────────────────┐     │
│                                    │             Grafana             │     │
│                                    │           (Port 3000)           │     │
│                                    └─────────────────────────────────┘     │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Configuration Specifications

### 4.1 OpenTelemetry Ingestion Pipeline

The OpenTelemetry Collector is configured via `config/otel/collector.yaml` with dedicated receiver, processor, and exporter chains.

- **Receivers:**
  - `otlp`: Listens on `0.0.0.0:4317` (gRPC) and `0.0.0.0:4318` (HTTP).
- **Processors:**
  - `batch`: Groups telemetry data to optimize transport efficiency and DB write load.
- **Exporters:**
  - `prometheus`: Exposes a scrapable HTTP endpoint at port `8889` for metric data.
  - `otlp/tempo`: Forwards incoming tracing directly to Tempo gRPC endpoint at `tempo:9095`.
  - `otlp/loki`: Forwards structured log records to Loki at `http://loki:3100/loki/api/v1/push`.

### 4.2 Log Collection & Processing

Grafana Alloy (replacing Promtail) acts as our container log harvester via `config/alloy/config.river`.

- **Discovery:** Targets the host container log directory using the Docker engine API via a local mount of `/var/run/docker.sock`.
- **Parsing:** Parses container log formats, extracts metadata (container name, image tag, compose project, service name), and structures them into Loki labels.
- **Exporting:** Forwards batch writes to Loki using the HTTP push protocol.

### 4.3 Data Source and Dashboard Provisioning

Grafana automatically configures datasources and preloads dashboards upon container boot via provisioning scripts:

- **Prometheus:** Configured as the default datasource on `http://prometheus:9090`.
- **Loki:** Mounted pointing to the Loki container at `http://loki:3100`.
- **Tempo:** Mounted on `http://tempo:3200` with direct traces-to-logs integration enabled (referencing the Loki datasource UID).
- **Dashboard Provisioning:** Scans `config/grafana/provisioning/dashboards/` for manifest maps linking to JSON templates in `/var/lib/grafana/dashboards/`.

---

## 5. Secret Management & Hardening

- **No Hardcoded Values:** Secrets like Grafana admin passwords and database credentials are never committed.
- **Environment Variable Substitution:** The `compose.yaml` utilizes environment variable bindings (such as `${GF_SECURITY_ADMIN_PASSWORD}`) sourced from a localized `.env` file (gitignored).
- **Network Isolation:** Only essential UI/ingestion ports are bound to external host interfaces. Intra-plane service-to-service communication is entirely contained within the bridge network.

---

## 6. Milestone Designs

### 6.1 Milestone 4: DORA & Ecosystem Integration Design (Implemented)

uFawkesObs is the observability substrate for DORA metrics. This section previously described a forward-looking design; M4-01 through M4-04 shipped (PRs #147, #148, plus recording-rule and dashboard work) and the design below reflects what is actually running, not a plan. The DORA data pipeline spans three planes:

- **uFawkesDORA (Compute Plane):** Ingestion API → Event Queue (Postgres) → Processor → Metric Compute Job. Owns DevLake as optional complementary visualization.
- **uFawkesRes (Resource Plane):** Shared PostgreSQL 17 + TimescaleDB on `fawkes-backbone-net`. Hosts `dora_metrics` database (schemas: `event_queue`, `raw_events`, `dora_snapshots`, `archetype_history`, `wellbeing_surveys`, `vsi_stage_breakdown`).
- **uFawkesObs (Observability Plane):** Prometheus (recording rules, alerting, time-series), Grafana (dashboards reading Prometheus + Postgres), Loki (raw event logs), a dedicated `otel-collector-dora` instance (ingestion from/to uFawkesDORA).

**Architecture in uFawkesObs (as built):**
- **Second OTel Collector:** `otel-collector-dora` compose service, gated behind the `dora` profile, configured via `config/otel/collector-dora.yaml`, connecting to `${DORA_OTEL_ENDPOINT:-http://ufawkesdora-ingestion:4318}`.
- **Recording Rules:** PromQL rules in `config/prometheus/rules/ufawkesobs-dora-metrics.yml` computing `dora:deployment_frequency:rate30d`, `dora:lead_time_hours:p50_30d`, `dora:fdrt_hours:p50_30d`, `dora:change_failure_rate:ratio30d`, `dora:rework_rate:ratio30d`.
- **DORA Dashboard:** Provisioned at `dashboards/platform/dora-metrics.json`, documented in `docs/adr/ADR-006-dora-metric-definitions.md`, with panels reading from Prometheus (trend lines) and PostgreSQL via the Postgres datasource plugin (current snapshots, archetype profile).
- **Network Attachment:** uFawkesObs joins `fawkes-backbone-net` (external name: `ufawkes-resources_fawkes-backbone-net`) to query uFawkesRes PostgreSQL for DORA snapshots. The `otel-collector-dora` service requires `DORA_POSTGRES_URL` as a fail-closed environment variable (no hardcoded fallback) — see §5.
- **Alertmanager Routing:** `dora_regression` and `leading_indicator` routes point to `SLACK_WEBHOOK_URL`.
- **Runtime-deployed status:** Deployed and running under the `dora` compose profile; exercised by the acceptance suite's DORA-dashboard checks (not yet by a dedicated live-system AC in the product discovery brief — see [`discovery-draft.md`](discovery-draft.md), whose current acceptance criterion covers the `core` profile only).

**What moved to other planes (no longer in uFawkesObs scope):**
- Apache DevLake → uFawkesDORA (optional, complementary to native ingestion)
- MySQL database → removed; DevLake uses uFawkesRes PostgreSQL

### 6.2 Milestone 5: Kubernetes & Helm Migration Design (Forward-Looking, Backlog)

- **Helm chart structure:** An umbrella Helm chart `helm/ufawkes-obs` containing separate sub-charts:
  - `prometheus-community/prometheus`
  - `grafana/grafana`
  - `grafana/loki`
  - `grafana/tempo`
  - `grafana/alloy`
- **NetworkPolicies:** Standard Kubernetes network segregation enforcing `restricted` security context.
- **Secret Integration:** Map External Secrets Operator (ESO) resources pointing to Vault paths rather than local Compose environment variable bindings.
