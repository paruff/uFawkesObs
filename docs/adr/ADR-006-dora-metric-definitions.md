# ADR-006: DORA Metric Definitions and Data Contract

**Status:** Accepted
**Date:** 2026-06-30
**Deciders:** uFawkesObs maintainers
**Issue:** [M4-01](https://github.com/paruff/uFawkesObs/issues/80)

---

## Context

uFawkesObs is the observability plane of the Fawkes IDP platform. It provides the telemetry substrate (metrics, logs, traces) that feeds into uFawkesDORA — the DORA metrics compute plane. uFawkesDORA requires a well-defined data contract to calculate the four DORA 2025 key metrics:

1. **Deployment Frequency** — How often code is deployed to production
2. **Lead Time for Changes** — Time from commit to production
3. **Change Failure Rate** — Percentage of deployments causing failures
4. **Mean Time to Restore (MTTR)** — Time to recover from a failure

uFawkesObs does not compute these metrics directly; it provides the raw telemetry (metrics, logs, traces) and derived recording rules that uFawkesDORA's ingestion API consumes. This ADR defines the data contract: what counts as a deployment, incident, and restoration within uFawkesObs telemetry, and the metric mappings uFawkesDORA expects.

---

## Decision

### 1. Deployment Definition

A **deployment** in uFawkesObs is identified by a **deployment span** emitted via OTLP by CI/CD systems (Jenkins, GitHub Actions, GitLab CI) or application deployment tools (ArgoCD, Flux, Helm).

**Required span attributes (OTel semantic conventions):**

| Attribute | Type | Required | Description |
|---|---|---|---|
| `cicd.pipeline.name` | string | Yes | Pipeline name (e.g., "ufawkesobs-main-deploy") |
| `cicd.pipeline.run.id` | string | Yes | Unique run ID (e.g., GitHub Actions run_id) |
| `deployment.environment` | string | Yes | Target environment: `production`, `staging`, `development` |
| `deployment.status` | string | Yes | `started`, `succeeded`, `failed`, `rolled_back` |
| `service.name` | string | Yes | Deployed service name (e.g., "otel-collector", "grafana") |
| `deployment.version` | string | Yes | Version/tag being deployed (e.g., "v1.2.3", "sha-abc123") |
| `deployment.strategy` | string | No | `rolling`, `blue_green`, `canary`, `recreate` |

**Deployment event semantics:**
- A deployment **starts** when a span with `deployment.status="started"` is received
- A deployment **succeeds** when a span with `deployment.status="succeeded"` is received for the same `cicd.pipeline.run.id`
- A deployment **fails** when a span with `deployment.status="failed"` is received
- A deployment is **rolled back** when a span with `deployment.status="rolled_back"` is received

**uFawkesDORA computes Deployment Frequency** by counting successful deployments to `production` per day/week.

---

### 2. Incident Definition

An **incident** is identified by an **Alertmanager alert** that fires and maps to a production service degradation.

**Required alert labels (Alertmanager/Prometheus):**

| Label | Type | Required | Description |
|---|---|---|---|
| `alertname` | string | Yes | Alert rule name (e.g., "UFawkesObsServiceDown") |
| `alert_domain` | string | Yes | Domain: `ufawkesobs-health`, `ai-capability`, `infra` |
| `severity` | string | Yes | `critical`, `warning`, `info` |
| `service` | string | Yes | Affected service (e.g., "prometheus", "grafana") |
| `environment` | string | Yes | `production`, `staging`, `development` |
| `instance` | string | No | Specific instance (e.g., "prometheus:9090") |

**Incident event semantics:**
- An incident **opens** when an alert with `severity="critical"` or `severity="warning"` fires for a production service
- An incident **closes** when the alert resolves (stops firing) and the `resolved` notification is received
- Incident duration = `resolved_at` - `fired_at`

**uFawkesDORA computes Change Failure Rate and MTTR** from incidents that:
- Have `environment="production"`
- Have `severity` in `["critical", "warning"]`
- Are linked to a deployment (via time correlation: incident opened within 24h of a deployment)

---

### 3. Restoration Definition

A **restoration** is the resolution of an incident, identified by the alert resolution notification.

**Restoration event semantics:**
- Triggered by Alertmanager `resolved` notification for a previously firing alert
- Restoration time = alert resolution timestamp
- MTTR = `restoration_time` - `incident_start_time`

---

### 4. DORA Metric Mappings (Recording Rules)

uFawkesObs provides the following Prometheus recording rules that uFawkesDORA consumes:

| Recording Rule | Type | Description | Source |
|---|---|---|---|
| `dora:deployment_frequency:rate30d` | Gauge | Successful production deployments per 30 days | Deployment spans |
| `dora:lead_time_hours:p50_30d` | Gauge | Median lead time (commit → production) over 30d | Deployment spans + commit timestamps |
| `dora:change_failure_rate:ratio30d` | Gauge | Failed deployments / total deployments (30d) | Deployment spans + incidents |
| `dora:mttr_hours:p50_30d` | Gauge | Median time to restore (hours) over 30d | Incident open/close times |

**Rule file location:** `config/prometheus/rules/ufawkesobs-dora-metrics.yml`

All rules are guarded with `or vector(0)` to prevent gaps during cold start.

---

### 5. Data Contract for uFawkesDORA Ingestion API

uFawkesObs forwards telemetry to uFawkesDORA via OTLP HTTP to the ingestion endpoint:

**Endpoint:** `http://ufawkesdora-ingestion:4318/v1/metrics` (OTLP HTTP)
**Protocol:** OTLP JSON Protobuf over HTTP
**Authentication:** Bearer token (`DORA_INGESTION_TOKEN`)

**Required metric attributes for uFawkesDORA:**

| Attribute | Description |
|---|---|
| `dora.event.type` | `deployment`, `incident`, `restoration` |
| `dora.event.timestamp` | RFC3339 timestamp |
| `dora.deployment.id` | Unique deployment identifier |
| `dora.incident.id` | Unique incident identifier |
| `dora.environment` | `production`, `staging`, `development` |
| `dora.service.name` | Service name |
| `dora.deployment.status` | `succeeded`, `failed`, `rolled_back` |
| `dora.incident.severity` | `critical`, `warning` |
| `dora.incident.duration_seconds` | Incident duration (for restoration events) |

**Forwarding mechanism:** uFawkesObs OTel Collector `exporters/otlphttp/dora` in `dora` compose profile.

---

### 6. Alerting Rules for DORA

uFawkesObs provides the following DORA-specific alert rules in `config/prometheus/rules/ufawkesobs-dora-alerts.yml`:

| Alert | Severity | Threshold | Description |
|---|---|---|---|
| `DORADeploymentFrequencyLow` | warning | `dora:deployment_frequency:rate30d < 1` | Deployments per 30d below 1 |
| `DORALeadTimeHigh` | warning | `dora:lead_time_hours:p50_30d > 24` | Median lead time > 24h |
| `DORAChangeFailureRateHigh` | warning | `dora:change_failure_rate:ratio30d > 0.15` | Change failure rate > 15% |
| `DORAChangeFailureRateCritical` | critical | `dora:change_failure_rate:ratio30d > 0.30` | Change failure rate > 30% |
| `DORAMTTRHigh` | warning | `dora:mttr_hours:p50_30d > 4` | Median MTTR > 4 hours |

All alerts carry `category: dora` label for routing.

---

### 7. Grafana Dashboard Provisioning

The DORA metrics dashboard is provisioned at:
- File: `dashboards/platform/dora-metrics.json`
- Grafana folder: `Platform`
- Datasources: `Prometheus` (UID: `prometheus`), `PostgreSQL` (UID: `ufawkesres-postgres`)

The dashboard shows the four DORA indicators with DORA 2025 performance bands (Elite/High/Medium/Low).

---

## Rationale

1. **Explicit definitions prevent ambiguity** — "Deployment" means different things to different teams. This ADR codifies the exact OTLP attributes and alert semantics uFawkesObs produces.

2. **Contract enables cross-plane integration** — uFawkesDORA's ingestion API can rely on a stable schema. Changes to this contract require an ADR update.

3. **DORA 2025 alignment** — The four metrics and their recording rules follow the DORA 2025 report definitions, with performance bands (Elite/High/Medium/Low) matching industry benchmarks.

4. **Separation of concerns** — uFawkesObs provides telemetry and recording rules; uFawkesDORA computes final metrics. This ADR defines the interface between them.

---

## Consequences

### Positive

- uFawkesDORA can reliably calculate DORA metrics from uFawkesObs telemetry
- CI/CD systems know exactly what OTLP attributes to emit for deployments
- Alert definitions are standardized across services
- Recording rules are versioned with uFawkesObs config

### Negative / Trade-offs

- CI/CD pipelines must be updated to emit the required deployment span attributes
- Existing deployments without these attributes will not be counted
- uFawkesDORA ingestion API must be available for the `dora` compose profile to work

### For Agents

- **Do not change deployment/incident attribute names** without updating this ADR
- The DORA recording rules file is `config/prometheus/rules/ufawkesobs-dora-metrics.yml`
- The DORA alert rules file is `config/prometheus/rules/ufawkesobs-dora-alerts.yml`
- The OTel Collector `dora` profile is in `config/otel/collector-dora.yaml`
- The Grafana dashboard is `dashboards/platform/dora-metrics.json`

---

## References

- DORA 2025 Report: <https://dora.dev/reports/2025/>
- OTel Semantic Conventions for CI/CD: <https://github.com/open-telemetry/semantic-conventions/blob/main/docs/ci-cd/README.md>
- OTel Semantic Conventions for Alerts: <https://github.com/open-telemetry/semantic-conventions/blob/main/docs/alert/README.md>
- uFawkesDORA Ingestion API spec: `docs/specification.md` (M4 section)
- Related ADRs: ADR-002 (Docker Compose scope), ADR-003 (GitOps scope), ADR-006 (this)

---

## Implementation Tasks

1. [ ] Create `docs/adr/ADR-006-dora-metric-definitions.md` (this file)
2. [ ] Add row to `docs/adr/README.md` index
3. [ ] Create `config/prometheus/rules/ufawkesobs-dora-metrics.yml` (recording rules)
4. [ ] Create `config/prometheus/rules/ufawkesobs-dora-alerts.yml` (alert rules)
5. [ ] Add `dora` profile to `compose.yaml` with OTel Collector exporter to uFawkesDORA
6. [ ] Create `config/otel/collector-dora.yaml` for DORA profile
7. [ ] Add Grafana Postgres datasource provisioning (`ufawkesres-postgres`)
8. [ ] Create `dashboards/platform/dora-metrics.json`
9. [ ] Update `docs/adr/README.md` index
10. [ ] Add Alertmanager route for `category: dora` alerts
