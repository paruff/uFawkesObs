# Acceptance Test Improvement Plan

**Status:** Draft v1.0
**Date:** 2026-06-29
**Author:** uFawkesAI Build Agent

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Guiding Principles](#2-guiding-principles)
3. [Phased Improvement Roadmap](#3-phased-improvement-roadmap)
4. [Phase 1: Unified Test Runtime & Pre-Merge Gate](#4-phase-1-unified-test-runtime--pre-merge-gate)
5. [Phase 2: Contract Testing Between Planes](#5-phase-2-contract-testing-between-planes)
6. [Phase 3: SLI/SLO Test Gates](#6-phase-3-slislo-test-gates)
7. [Phase 4: Synthetic Workload Generator](#7-phase-4-synthetic-workload-generator)
8. [Phase 5: Chaos & Failure Injection](#8-phase-5-chaos--failure-injection)
9. [Phase 6: Evidence Pipeline & Documentation](#9-phase-6-evidence-pipeline--documentation)
10. [Phase 7: Post-Merge Comprehensive Suite](#10-phase-7-post-merge-comprehensive-suite)
11. [CI/CD Integration Summary](#11-cicd-integration-summary)
12. [Success Metrics](#12-success-metrics)
13. [Deprecation Path](#13-deprecation-path)

---

## 1. Current State Assessment

### What Exists Today

| Layer | Type | Location | Lines | What It Tests | Run When |
|---|---|---|---|---|---|
| Shell E2E (OTel pipeline) | Shell script | `tests/acceptance/observability-pipeline/test-otel-pipeline.sh` | ~492 | OTel Collector health, Prometheus scraping, Grafana datasource, E2E metric query | `make test-acceptance` or CI |
| Shell E2E (Loki logs) | Shell script | `tests/acceptance/observability-pipeline/test-loki-logs.sh` | ~436 | Loki health, Alloy health, log ingestion, log labels, LogQL, trace correlation config | `make test-acceptance` or CI |
| Shell E2E (Alertmanager) | Shell script | `tests/acceptance/observability-pipeline/test-alertmanager.sh` | ~314 | Alertmanager health, Prometheus→AM connection, alert rules, API, config, routing | `make test-acceptance` or CI |
| Shell E2E (Dashboards) | Shell script | `tests/acceptance/observability-pipeline/test-dashboard-validation.sh` | ~436 | Infrastructure ready, dashboard provisioning, metrics/logs/traces data availability, rendering | `make test-acceptance` or CI |
| Shell orchestrator | Shell script | `tests/acceptance/e2e-runner.sh` | ~269 | Stack lifecycle (start/stop), scenario dispatch (full-pipeline, integration-tests, quick-check) | CI or manual |
| Python integration tests | pytest | `tests/integration/test_*.py` (6 files) | ~2,000+ combined | Prometheus scraping, OTel Collector health/receivers/exporters/processors, Grafana, Tempo, Loki, dashboards | CI `ci-tests.yml` |
| Python E2E tests | pytest | `tests/e2e/test_telemetry_flow.py` | ~555 | Synthetic OTel trace/metric generation, Prometheus→Grafana flow, Tempo trace query, correlation | CI or manual |
| Python unit tests | pytest | `tests/unit/test_*.py` (10 files) | ~2,000+ combined | Config validation (YAML schema, port correctness, version pins), compose verification | CI `ci-tests.yml` |

### Identified Gaps

| Gap | Severity | Evidence |
|---|---|---|
| **No contract testing between planes** | 🔴 Critical | No test verifies that uFawkesPipe, uFawkesDevX, or a generic external app can send OTLP telemetry through `observability-lab` network and see it in Grafana |
| **Trace pipeline untested end-to-end** | 🔴 Critical | OTel→Tempo path tested only for readiness, not with actual synthetic traces flowing through the full pipeline |
| **No SLI/SLO measurement** | 🟡 High | No test measures ingestion latency, scrape completeness, or data freshness. Telemetry quality is assumed, not verified |
| **No chaos/failure injection** | 🟡 High | System behavior under failure (Loki restart, network partition) is untested |
| **Shell scripts duplicate Python tests** | 🟡 High | `test-otel-pipeline.sh` overlaps significantly with `tests/integration/test_otel_collector.py` and `tests/integration/test_prometheus_scraping.py` |
| **Evidence not consumed** | 🟢 Medium | Reports generated but never feed runbooks, dashboards, or onboarding docs |
| **No pre/post-merge split** | 🟢 Medium | All tests run together. No fast pre-merge smoke gate, no comprehensive post-merge suite |
| **No CI workflow for post-merge acceptance** | 🟢 Medium | `ci-tests.yml` runs on PR. No workflow runs acceptance after merge before deployment |

### Current CI Flow

```
PR → ci-pipeline.yml → preflight → lint → security → build → ci-tests.yml (unit + compose-smoke + integration) → merge
                                                           ↓ main
                                                     deploy.yml (SSH to target host)
```

No acceptance test runs between merge and deployment.

---

## 2. Guiding Principles

1. **Test execution split:**
   - **Pre-merge (fast, <3 min):** Smoke tests, contract tests, critical health checks. Required to merge.
   - **Post-merge (comprehensive, <15 min):** Full SLOs, chaos, evidence generation. Runs after merge, gates deployment.

2. **Unified runtime:** Replace 4 disjoint shell scripts with a single `ObservabilityStack` Python class that manages compose lifecycle and provides typed clients (PromQL, Loki, Tempo, Grafana, OTLP).

3. **Consumer-driven contracts:** Invest in contract tests that prove telemetry flows end-to-end from external planes. Deprecate redundant structural tests (~50% reduction).

4. **Evidence is first-class output:** Every test captures its inputs/outputs as structured JSON. Post-processing generates runbook snippets, dashboard queries, and onboarding examples.

5. **SLO gates are post-merge only:** Latency measurement requires sampling windows too slow for pre-merge. Pre-merge gates are binary (reachability, contract compliance).

6. **Chaos is nightly-only:** Failure injection tests require stack restarts. Run on schedule, not gating any deployment.

7. **pytest-bdd with markers:** All acceptance tests use Gherkin feature files with `@smoke` (pre-merge) and `@full` (post-merge) markers.

---

## 3. Phased Improvement Roadmap

```
Phase 1: Unified Runtime & Pre-Merge Gate        Week 1-2   [🔴 Critical]
Phase 2: Contract Testing Between Planes          Week 3-4   [🔴 Critical]
Phase 3: SLI/SLO Test Gates                       Week 4-6   [🟡 High]
Phase 4: Synthetic Workload Generator             Week 5-7   [🟡 High]
Phase 5: Chaos & Failure Injection                Week 6-8   [🟢 Medium]
Phase 6: Evidence Pipeline & Documentation        Week 7-9   [🟢 Medium]
Phase 7: Post-Merge Comprehensive Suite CI         Week 8-9   [🔴 Critical]
```

---

## 4. Phase 1: Unified Test Runtime & Pre-Merge Gate

**Goal:** Single, unified test runtime that eliminates shell script fragmentation and provides the foundation for all subsequent phases.

### 4.1 Shell Scripts → pytest-bdd Migration

| Current Shell Script | New pytest-bdd Equivalent | Marker | Priority |
|---|---|---|---|
| `test-otel-pipeline.sh` | `features/otel_pipeline.feature` — 3 scenarios (health, scraping, Grafana query) | `@smoke` | 🔴 Critical |
| `test-loki-logs.sh` | `features/loki_logs.feature` — 3 scenarios (health, ingestion, LogQL) | `@smoke` | 🔴 Critical |
| `test-alertmanager.sh` | `features/alertmanager.feature` — 2 scenarios (health, rules loaded) | `@smoke` | 🟡 High |
| `test-dashboard-validation.sh` | `features/dashboards.feature` — 2 scenarios (provisioned, renders) | `@smoke` | 🟡 High |

### 4.2 ObservabilityStack Python Class

Create `tests/acceptance/runtime.py` with a unified `ObservabilityStack` class:

```python
class ObservabilityStack:
    """Manages the uFawkesObs Docker Compose stack and provides typed clients."""

    def __init__(self, compose_dir: str = "."):
        self.compose_dir = compose_dir

    # Lifecycle
    def start(self, profiles: list[str] = ["core"]) -> None
    def stop(self) -> None
    def restart_service(self, service: str) -> None
    def wait_for_healthy(self, timeout: int = 120) -> dict[str, bool]

    # Typed clients
    def promql(self) -> PromQLClient       # Prometheus API v1
    def loki(self) -> LokiClient           # Loki HTTP API
    def tempo(self) -> TempoClient         # Tempo HTTP API
    def grafana(self) -> GrafanaClient     # Grafana API + datasource queries
    def otlp(self) -> OTLPClient           # OTel Collector OTLP sender

    # Synthetic workload
    def send_trace(self, name: str, spans: int = 3) -> str       # Returns trace_id
    def send_metric(self, name: str, value: float, labels: dict) -> str
    def send_log(self, body: str, labels: dict) -> None
```

### 4.3 Test Markers

```python
# conftest.py
# @smoke  → runs pre-merge (fast, <3 min total)
# @full   → runs post-merge (comprehensive, <15 min total)
# @chaos  → runs nightly only
```

### 4.4 Pre-Merge Gate Scenarios

```gherkin
@smoke
Feature: Core Stack Health (OBS-SMOKE-001)
  Scenario: All core services are healthy
    Given the core stack is running
    Then all services should report healthy within 60 seconds
    And the Grafana API should return 200

  Scenario: OTel Collector metrics reachable
    Given the core stack is running
    Then the OTel Collector metrics endpoint should return self-metrics
    And Prometheus should report the OTel Collector target as "up"

  Scenario: Grafana datasources provisioned
    Given the core stack is running
    Then Grafana should have datasources for Prometheus, Loki, Tempo, and Alertmanager

@smoke
Feature: Log Pipeline Health (OBS-SMOKE-002)
  Scenario: Loki is ingesting logs
    Given the core stack has been running for 30 seconds
    Then Loki should report at least 1 log stream
    And LogQL query {job="docker"} should return results

@smoke
Feature: Trace Pipeline Health (OBS-SMOKE-003)
  Scenario: Tempo is ready
    Given the core stack is running
    Then the Tempo /ready endpoint should return 200
```

### 4.5 Deliverables

| File | Purpose |
|---|---|
| `tests/acceptance/runtime.py` | `ObservabilityStack` class with typed clients |
| `tests/acceptance/conftest.py` | Shared fixtures, markers, `ObservabilityStack` fixture |
| `tests/acceptance/features/otel_pipeline.feature` | 3 @smoke scenarios |
| `tests/acceptance/features/loki_logs.feature` | 3 @smoke scenarios |
| `tests/acceptance/features/alertmanager.feature` | 2 @smoke scenarios |
| `tests/acceptance/features/dashboards.feature` | 2 @smoke scenarios |
| `tests/acceptance/requirements.txt` | Python dependencies (pytest, pytest-bdd, requests, opentelemetry-sdk, etc.) |

### 4.6 Deprecation Plan

After Phase 1 is validated (all @smoke tests passing in CI):

- [ ] Remove `tests/acceptance/observability-pipeline/test-otel-pipeline.sh`
- [ ] Remove `tests/acceptance/observability-pipeline/test-loki-logs.sh`
- [ ] Remove `tests/acceptance/observability-pipeline/test-alertmanager.sh`
- [ ] Remove `tests/acceptance/observability-pipeline/test-dashboard-validation.sh`
- [ ] Remove `tests/acceptance/e2e-runner.sh`
- [ ] Update `Makefile` to replace `make test-acceptance` with `pytest tests/acceptance/ -m smoke`

### 4.7 Acceptance Criteria

- [ ] `pytest tests/acceptance/ -m smoke --stack=existing` completes in <3 min
- [ ] All 4 shell E2E scripts migrated to pytest-bdd feature files
- [ ] `ObservabilityStack` class fully implemented with typed clients
- [ ] CI `ci-tests.yml` updated to run `@smoke` tests pre-merge instead of shell scripts
- [ ] Shell scripts deprecated with warning comments

---

## 5. Phase 2: Contract Testing Between Planes

**Goal:** Prove that external consumers (uFawkesPipe, uFawkesDevX, generic apps) can send OTLP telemetry to uFawkesObs and see it queryable.

### 5.1 Multi-Plane Contract Scenarios

```gherkin
@smoke @contract
Feature: Multi-Plane Telemetry Contract (OBS-CONTRACT-001-003)

  Background:
    Given the observability-lab network is running
    And uFawkesObs core stack is healthy

  Scenario: OBS-CONTRACT-001 — External OTLP trace ingested by Tempo
    When a test container joins the "observability-lab" network
    And it sends a synthetic OTLP trace to "otel-collector:4317" via gRPC
    Then the trace should be queryable via Tempo API within 15s
    And the trace should have all 3 spans preserved

  Scenario: OBS-CONTRACT-002 — External OTLP metric scraped by Prometheus
    When a test container joins the "observability-lab" network
    And it exports a counter metric "test_requests_total" via OTLP HTTP
    Then Prometheus should contain "test_requests_total" within 30s
    And the metric should have labels: "instance", "job", "service_name"

  Scenario: OBS-CONTRACT-003 — External OTLP log indexed by Loki
    When a test container joins the "observability-lab" network
    And it sends a structured JSON log via OTLP logs signal
    Then the log should be queryable in Loki within 15s
    And the log body should parse as valid JSON with original keys preserved
```

### 5.2 Cross-Plane Integration Test

```gherkin
@smoke @contract
Feature: Cross-Plane Datasource Resolution (OBS-CONTRACT-004)

  Scenario: External plane datasources resolve correctly
    Given the uFawkesObs stack is running
    When an external plane queries Grafana API for datasources
    Then the Prometheus datasource should use "http://prometheus:9090"
    And the Tempo datasource should use "http://tempo:3200"
    And the Loki datasource should use "http://loki:3100"
    And the Alertmanager datasource should use "http://alertmanager:9093"
```

### 5.3 Test Infrastructure

- A lightweight test container (or Python process) joins `observability-lab` network
- Sends OTLP telemetry via gRPC (4317) and HTTP (4318)
- Queries Prometheus/Loki/Tempo APIs directly (not via Grafana) to verify ingestion
- Uses the same `docker-compose.integration.yml` pattern documented in `docs/multi-stack-integration.md`

### 5.4 Deliverables

| File | Purpose |
|---|---|
| `tests/acceptance/features/multi_plane_contract.feature` | Contract test scenarios |
| `tests/acceptance/steps/multi_plane_steps.py` | Step implementations for contract tests |
| `tests/acceptance/workloads/synthetic_trace.py` | Generates realistic trace with 3-5 spans |
| `tests/acceptance/workloads/synthetic_metric.py` | Counter + histogram with known increments |
| `tests/acceptance/workloads/synthetic_log.py` | Structured JSON log body |

### 5.5 Acceptance Criteria

- [ ] All 4 contract scenarios pass against a running stack
- [ ] Traces flow: test container → OTel Collector (gRPC) → Tempo → queryable via API
- [ ] Metrics flow: test container → OTel Collector (HTTP) → Prometheus → queryable via API
- [ ] Logs flow: test container → OTel Collector (OTLP logs) → Loki → queryable via API
- [ ] Cross-plane integration test container can join `observability-lab` network

---

## 6. Phase 3: SLI/SLO Test Gates

**Goal:** Measure and gate on telemetry system quality — not just availability.

### 6.1 SLO Definition

| SLI | SLO | Method | Test Type |
|---|---|---|---|
| **OTLP → Prometheus scrape latency** | p99 < 30s | Send metric, poll Prometheus until value appears, measure delta | @full |
| **Log ingestion latency** | p99 < 15s | Send log via OTLP, measure timestamp delta in Loki | @full |
| **Trace ingestion latency** | p99 < 20s | Send trace via OTLP, query Tempo, measure delta | @full |
| **Scrape completeness** | 100% of configured targets UP | Query `up` metric, assert all core targets have value 1 | @full |
| **Grafana datasource health** | 100% datasources reachable | Query Grafana API for each datasource, check health | @full |
| **Dashboard data freshness** | All pre-loaded dashboards show data within 5m | Query each dashboard's panels, check non-empty results | @full |

### 6.2 Test Implementation

```python
# tests/acceptance/slos/test_ingestion_latency.py

def test_otel_to_prometheus_latency(live_stack: ObservabilityStack):
    """OBS-SLI-001: OTLP → Prometheus scrape latency < 30s p99."""
    client = live_stack.otlp()
    prom = live_stack.promql()

    # Emit counter with unique value for correlation
    test_value = int(time.time() * 1000)
    client.emit_counter("test_ingest_latency", test_value,
                         labels={"test_run": str(test_value)})

    # Poll Prometheus until value appears
    latency = poll_for_value(
        prom, f'test_ingest_latency_total{{test_run="{test_value}"}}',
        expected=test_value, timeout=60
    )

    assert latency < 30_000, \
        f"Ingestion latency {latency}ms exceeds SLO of 30,000ms"
    capture_evidence("ingestion_latency", {"latency_ms": latency, "test_value": test_value})
```

### 6.3 SLO Report Generation

Each SLO test captures its measurement as evidence. After all SLO tests run, a report is generated:

```python
# tests/acceptance/evidence/slo_report.py

def generate_slo_report(results: list[SloResult]) -> str:
    """Generate SLO compliance report as markdown."""
    # Output: tests/acceptance/evidence/slo-report-{timestamp}.md
```

### 6.4 Deliverables

| File | Purpose |
|---|---|
| `tests/acceptance/features/slo_gates.feature` | 6 SLO test scenarios |
| `tests/acceptance/steps/slo_steps.py` | SLO measurement step implementations |
| `tests/acceptance/evidence/slo_report.py` | SLO compliance report generator |

### 6.5 Acceptance Criteria

- [ ] All 6 SLO tests pass against a running stack (or report violations)
- [ ] SLO report generated after test run with latency histograms
- [ ] SLO violations produce clear error messages with measured vs expected values
- [ ] Evidence captured for each SLO measurement

---

## 7. Phase 4: Synthetic Workload Generator

**Goal:** Generate realistic, reproducible telemetry for contract and SLO tests.

### 7.1 Workload Types

| Workload | Signals | Pattern | Use Case |
|---|---|---|---|
| **Web API simulation** | Traces + Metrics | HTTP handler pattern, spans for `handler`, `db_query`, `ext_call` | Standard OTLP workload |
| **Batch job simulation** | Traces + Logs | Background worker, spans for `process_item`, `write_result` | CI pipeline emulation |
| **Health check** | Metrics | `up` metric, `scrape_duration_seconds` | Prometheus scrape target |
| **Log emitter** | Logs | Structured JSON logs at configurable rate | Loki ingestion testing |
| **DORA event generator** | Traces | Deployment, incident, and lead-time spans | DORA metric testing |

### 7.2 Implementation

```python
# tests/acceptance/workloads/web_api.py

class WebApiWorkload:
    """Simulates a web application sending OTLP telemetry."""

    def __init__(self, otlp_endpoint: str):
        self.tracer = ...
        self.meter = ...

    def simulate_request(self, path: str, duration_ms: int = 50) -> str:
        """Simulate a web request, return trace_id."""
        with self.tracer.start_as_current_span(f"GET {path}") as span:
            trace_id = format(span.get_span_context().trace_id, "032x")
            span.set_attribute("http.method", "GET")
            span.set_attribute("http.route", path)

            with self.tracer.start_as_current_span("db.query") as db_span:
                db_span.set_attribute("db.system", "postgresql")
                time.sleep(duration_ms / 1000)

            self.meter.create_counter("http_requests_total").add(1, {
                "method": "GET", "path": path, "status": "200"
            })

        return trace_id
```

### 7.3 Reusable Across Test Phases

- Phase 2 (Contract tests): Use workload generators to send telemetry
- Phase 3 (SLO tests): Use workload generators with known metrics
- Phase 5 (Chaos tests): Use workload generators to generate traffic during failure injection

### 7.4 Deliverables

| File | Purpose |
|---|---|
| `tests/acceptance/workloads/__init__.py` | Workload registry |
| `tests/acceptance/workloads/web_api.py` | Web API simulation |
| `tests/acceptance/workloads/batch_job.py` | Batch job simulation |
| `tests/acceptance/workloads/log_emitter.py` | Structured log emitter |
| `tests/acceptance/workloads/dora_events.py` | DORA event generator |

---

## 8. Phase 5: Chaos & Failure Injection

**Goal:** Validate system behavior under failure — not just idle-healthy.

### 8.1 Chaos Scenarios

| Scenario | Method | Expected Behavior | Type |
|---|---|---|---|
| **Loki goes down** | `docker compose stop loki` | Alloy buffers logs, re-plays when Loki returns. No data loss. | @chaos |
| **Prometheus goes down** | `docker compose stop prometheus` | OTel Collector buffers metrics, backfills on restart. Remote Write reconnects. | @chaos |
| **OTel Collector restarts** | `docker compose restart otel-collector` | Exporters retry with backoff. Tempo/Loki see no gap > 60s. | @chaos |
| **Network partition** | Docker network disconnect | Exporters detect disconnect, exponential backoff, reconnect when restored. | @chaos |
| **Grafana loses datasource** | Remove datasource provisioned file | Grafana continues serving cached dashboards. New queries fail gracefully. | @chaos |

### 8.2 Test Scenarios

```gherkin
@chaos
Feature: Chaos Resilience (OBS-CHAOS-001-005)

  Background:
    Given the core stack is running
    And synthetic telemetry is being generated

  Scenario: OBS-CHAOS-001 — Log pipeline survives Loki restart
    When I stop the "loki" service
    Then Alloy should continue running and buffering logs
    When I start the "loki" service after 30s
    Then all buffered logs should be queryable in Loki within 60s
    And the log count after restart should match the count before restart (+/- 5%)

  Scenario: OBS-CHAOS-002 — Metrics pipeline survives Prometheus restart
    When I stop the "prometheus" service
    Then existing metrics should still be queryable via Grafana (cached)
    When I start the "prometheus" service after 30s
    Then Prometheus should resume scraping all targets within 60s
    And metric gaps should not exceed 90s

  Scenario: OBS-CHAOS-003 — OTel Collector restart is transparent
    Given synthetic telemetry is being generated
    When I restart the "otel-collector" service
    Then the trace pipeline should resume within 30s
    And new traces should be queryable in Tempo within 30s of restart

  Scenario: OBS-CHAOS-004 — Network partition self-heals
    When I disconnect the "otel-collector" from the observability network
    Then the OTel Collector should log connection errors (not crash)
    When I reconnect the "otel-collector" to the observability network after 20s
    Then all telemetry pipelines should resume within 30s
```

### 8.3 Importance of Synthetic Workload (Phase 4)

Chaos tests require a continuously running synthetic workload to measure impact. Phase 4 must be complete before Phase 5 has value.

### 8.4 Deliverables

| File | Purpose |
|---|---|
| `tests/acceptance/features/chaos_resilience.feature` | 5 chaos scenarios |
| `tests/acceptance/steps/chaos_steps.py` | Failure injection step implementations |
| `tests/acceptance/evidence/chaos_report.py` | Recovery timeline evidence generator |

### 8.5 Acceptance Criteria

- [ ] All 5 chaos scenarios pass (or produce documented known failure modes)
- [ ] Recovery timelines captured as Mermaid sequence diagrams
- [ ] Data loss measured and reported for each scenario

---

## 9. Phase 6: Evidence Pipeline & Documentation

**Goal:** Every test execution generates consumable artifacts that feed runbooks, dashboards, and onboarding docs.

### 9.1 Evidence Artifacts

| Artifact | Format | Consumer |
|---|---|---|
| **OTLP payload exchange** (request/response) | JSON | Runbook examples, troubleshooting guides |
| **Grafana API responses** (dashboard panels, Explore queries) | JSON | Screenshot generation, dashboard validation |
| **Prometheus scrape targets** | JSON/CSV | Target inventory, configuration drift detection |
| **Failure recovery trace** (timeline of chaos test) | Mermaid sequence diagram | Incident response runbooks |
| **SLO compliance report** (latency histograms, pass/fail per SLI) | Markdown + JSON | Weekly platform review |

### 9.2 Evidence Collector

```python
# tests/acceptance/evidence/collector.py

class EvidenceCollector:
    """Collects and stores test evidence as structured artifacts."""

    def capture_otlp_payload(self, endpoint: str, payload: dict) -> str:
        """Save OTLP payload and return path."""

    def capture_grafana_response(self, query: str, response: dict) -> str:
        """Save Grafana API response."""

    def capture_prometheus_targets(self, targets: list) -> str:
        """Save Prometheus scrape target inventory."""

    def generate_recovery_timeline(self, events: list[dict]) -> str:
        """Generate Mermaid sequence diagram from chaos test events."""

    def generate_slo_report(self, results: list[SloResult]) -> str:
        """Generate SLO compliance report."""

    def generate_runbook_snippets(self) -> str:
        """
        Convert latest passing evidence into runbook examples:
        - "Missing traces? Here's a known-good OTLP payload"
        - "Ingestion slow? Here's the expected p99 latency"
        - "Dashboard empty? Here's the query that should return data"
        """
```

### 9.3 Evidence → Documentation Pipeline

```python
# tests/acceptance/evidence/generate_runbook.py

def generate_runbook_snippets(evidence: EvidenceBundle) -> str:
    """Turn test evidence into actionable runbook examples."""
    trace = evidence.get("trace_query_example")
    latency = evidence.get("ingestion_latency_p99")
    panel_query = evidence.get("dashboard_panel_query")

    return f"""
## Debugging: Missing Telemetry from External Planes

**Quick check query** (takes < 5s):
```promql
{panel_query}
```

**Expected:** Non-empty result within 30s of deployment.
**If empty:** Check container is on `observability-lab` network.
**If slow (>15s):** Expected p99 latency is {latency}ms. Check OTel Collector resources.

**Example OTLP payload** (from contract test):
```json
{trace}
```
"""
```

### 9.4 Deliverables

| File | Purpose |
|---|---|
| `tests/acceptance/evidence/collector.py` | Evidence collection base class |
| `tests/acceptance/evidence/generate_runbook.py` | Runbook snippet generator |
| `tests/acceptance/evidence/slo_report.py` | SLO compliance report generator |
| `docs/acceptance-evidence/` | Committed evidence from latest post-merge run |

---

## 10. Phase 7: Post-Merge Comprehensive Suite

**Goal:** Right test runs at the right time with the right feedback loop.

### 10.1 CI/CD Workflow Design

```yaml
# .github/workflows/ci-acceptance-smoke.yml — Pre-merge (fast, < 3 min)
name: Acceptance Smoke (Pre-Merge)

on:
  pull_request:
    branches: [main]

jobs:
  acceptance-smoke:
    name: Acceptance Smoke
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r tests/acceptance/requirements.txt
      - name: Create data directories
        run: |
          mkdir -p data/{tempo,loki,alloy,prometheus,alertmanager,grafana}
          chmod -R 777 data/
      - name: Start core stack
        run: docker compose --profile core up -d
      - name: Wait for healthy
        run: |
          python -c "
          import time, requests
          services = ['http://localhost:9090/-/ready', 'http://localhost:3100/ready',
                      'http://localhost:3200/ready', 'http://localhost:3000/api/health',
                      'http://localhost:9093/-/healthy', 'http://localhost:12345/-/ready']
          for url in services:
              for i in range(60):
                  try:
                      r = requests.get(url, timeout=5)
                      if r.status_code == 200:
                          print(f'✅ {url}')
                          break
                  except: pass
                  time.sleep(2)
      - name: Run smoke tests
        run: |
          pytest tests/acceptance/ -m "smoke" -v \
            --junit-xml=reports/acceptance-smoke.xml \
            --evidence-dir=reports/acceptance-smoke-evidence
      - name: Upload smoke evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: acceptance-smoke-evidence
          path: reports/acceptance-smoke-evidence/
      - name: Shutdown
        if: always()
        run: docker compose --profile core down -v
```

```yaml
# .github/workflows/ci-acceptance-full.yml — Post-merge (comprehensive, < 15 min)
name: Acceptance Full (Post-Merge)

on:
  push:
    branches: [main]

jobs:
  acceptance-full:
    name: Acceptance Full Suite
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r tests/acceptance/requirements.txt
      - name: Create data directories
        run: |
          mkdir -p data/{tempo,loki,alloy,prometheus,alertmanager,grafana}
          chmod -R 777 data/
      - name: Start full stack with telemetry generator
        run: docker compose --profile core --profile apps up -d
      - name: Wait for healthy
        run: |
          python -c "
          import time, requests
          services = ['http://localhost:9090/-/ready', 'http://localhost:3100/ready',
                      'http://localhost:3200/ready', 'http://localhost:3000/api/health',
                      'http://localhost:9093/-/healthy', 'http://localhost:12345/-/ready',
                      'http://localhost:5001/health']
          for url in services:
              for i in range(60):
                  try:
                      r = requests.get(url, timeout=5)
                      if r.status_code == 200:
                          print(f'✅ {url}')
                          break
                  except: pass
                  time.sleep(2)
      - name: Run full acceptance suite
        run: |
          pytest tests/acceptance/ -m "full" -v \
            --junit-xml=reports/acceptance-full.xml \
            --evidence-dir=reports/acceptance-full-evidence
      - name: Generate runbook snippets
        run: |
          python tests/acceptance/evidence/generate_runbook.py \
            --evidence-dir=reports/acceptance-full-evidence \
            --output=reports/runbook-snippets.md
      - name: Generate SLO report
        run: |
          python tests/acceptance/evidence/slo_report.py \
            --evidence-dir=reports/acceptance-full-evidence \
            --output=reports/slo-report.md
      - name: Upload full evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: acceptance-full-evidence
          path: |
            reports/acceptance-full-evidence/
            reports/runbook-snippets.md
            reports/slo-report.md
      - name: Shutdown
        if: always()
        run: docker compose --profile core --profile apps down -v
```

```yaml
# .github/workflows/ci-chaos-nightly.yml — Nightly Chaos
name: Chaos Nightly

on:
  schedule:
    - cron: "0 2 * * *"  # 2am daily

jobs:
  chaos-tests:
    name: Chaos Resilience Tests
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      # ... same pattern but with -m "chaos"
      - name: Run chaos tests
        run: pytest tests/acceptance/ -m "chaos" -v
```

### 10.2 Pipeline Integration

Update `ci-pipeline.yml` to incorporate the new workflows:

```yaml
# Updated ci-pipeline.yml
tests:
  name: Tests
  needs: [build]
  uses: ./.github/workflows/ci-acceptance-smoke.yml  # Was: ci-tests.yml

# New stage: Post-merge acceptance (called from deploy.yml or separate workflow)
acceptance-full:
  name: Full Acceptance
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  uses: ./.github/workflows/ci-acceptance-full.yml
```

### 10.3 Deployment Gate

The `deploy.yml` workflow should wait for post-merge acceptance before deploying:

```yaml
# deploy.yml — Updated
deploy-config-reload:
  name: Deploy (config reload)
  needs: [detect-changes, acceptance-full]  # Wait for full acceptance
  ...
```

> **Note:** Adding `acceptance-full` as a dependency of `deploy.yml` increases time-to-deployment by ~15 minutes. This is intentional — comprehensive testing before deployment is the trade-off for confidence. If this delay is unacceptable, run acceptance in parallel with deploy and gate on health check results.

### 10.4 Deliverables

| File | Purpose |
|---|---|
| `.github/workflows/ci-acceptance-smoke.yml` | Pre-merge smoke test workflow |
| `.github/workflows/ci-acceptance-full.yml` | Post-merge full acceptance workflow |
| `.github/workflows/ci-chaos-nightly.yml` | Nightly chaos test workflow |
| Update `.github/workflows/ci-pipeline.yml` | Point `tests` stage to smoke workflow |
| Update `.github/workflows/deploy.yml` | Add `acceptance-full` as dependency |

### 10.5 Acceptance Criteria

- [ ] Pre-merge smoke tests complete in <5 min total (including stack startup)
- [ ] Post-merge full suite completes in <15 min total
- [ ] Evidence artifacts are uploaded for every run
- [ ] Runbook snippets and SLO reports are generated from evidence
- [ ] Nightly chaos runs on schedule and reports results

---

## 11. CI/CD Integration Summary

```
PR (push)
  │
  ├── ci-pipeline.yml
  │     ├── preflight          (reusable: commit format, PR size, secrets)
  │     ├── lint               (reusable: yamllint, shellcheck)
  │     ├── security           (reusable: Gitleaks, Trivy, dependency review)
  │     ├── build              (reusable: config validation, version pins)
  │     └── tests              (uses ci-acceptance-smoke.yml)
  │           ├── unit-tests   (config validation)
  │           └── smoke        (@smoke tests: health, contracts, critical SLOs)
  │
  └── merge to main
        │
        ├── ci-acceptance-full.yml   ← NEW (comprehensive check before deploy)
        │     ├── full acceptance    (@full tests: full SLOs, dashboards)
        │     ├── evidence           (runbook snippets, SLO report)
        │     └── generate docs      (committed to docs/acceptance-evidence/)
        │
        ├── deploy.yml               (runs in parallel or after acceptance)
        │     ├── compose restart    (if compose.yaml changed)
        │     └── config reload      (if config changed)
        │
        └── ci-chaos-nightly.yml     ← NEW (nightly scheduled)
              └── chaos tests        (@chaos tests: failure injection)
```

### Timing Budget

| Pipeline Stage | Time Budget | Notes |
|---|---|---|
| Pre-merge smoke (including stack start) | <5 min | Parallelizable with other PR checks |
| Post-merge full acceptance | <15 min | Runs before or alongside deploy |
| Nightly chaos | <30 min | Scheduled, non-gating |

---

## 12. Success Metrics

| Metric | Current | Target (Week 9) |
|---|---|---|
| **Pre-merge test duration** | ~4 min (shell scripts + integration) | <3 min (pytest-bdd @smoke) |
| **Post-merge test duration** | N/A | <15 min (pytest-bdd @full) |
| **Contract test coverage** | 0 scenarios | 4 scenarios across 3 planes |
| **SLO gates** | 0 | 6 SLIs with automated gates |
| **Chaos scenarios** | 0 | 5 failure modes tested |
| **Evidence artifacts per run** | ~5 JSON snippets | ~20+ artifacts across runbooks, docs, dashboards |
| **CI flake rate** | Unknown (not tracked) | <1% |
| **Shell script lines** | ~1,678 (4 scripts + runner) | 0 (fully migrated) |
| **Python test lines (acceptance)** | 0 (pyc only) | ~2,000 (pytest-bdd feature files + steps) |

---

## 13. Deprecation Path

### Phase 1 Completion

| File | Action | Reason |
|---|---|---|
| `tests/acceptance/observability-pipeline/test-otel-pipeline.sh` | Remove | Replaced by `features/otel_pipeline.feature` |
| `tests/acceptance/observability-pipeline/test-loki-logs.sh` | Remove | Replaced by `features/loki_logs.feature` |
| `tests/acceptance/observability-pipeline/test-alertmanager.sh` | Remove | Replaced by `features/alertmanager.feature` |
| `tests/acceptance/observability-pipeline/test-dashboard-validation.sh` | Remove | Replaced by `features/dashboards.feature` |
| `tests/acceptance/e2e-runner.sh` | Remove | Replaced by `ObservabilityStack` class |
| `tests/acceptance/observability-pipeline/reports/` | Keep (legacy) | Historical reference |

### Phase 2-3 Completion

| File | Action | Reason |
|---|---|---|
| `tests/integration/test_otel_collector.py` | Deprecate | Overlap with `features/otel_pipeline.feature` |
| `tests/integration/test_prometheus_scraping.py` | Deprecate | Overlap with contract tests |
| `tests/integration/test_loki_integration.py` | Deprecate | Overlap with `features/loki_logs.feature` |
| `tests/integration/test_tempo_integration.py` | Keep (migrate steps) | Only Tempo-specific tests, migrate to steps |
| `tests/integration/test_grafana_integration.py` | Keep (migrate steps) | Only Grafana-specific tests, migrate to steps |
| `tests/integration/test_dashboards.py` | Deprecate | Overlap with `features/dashboards.feature` |

### Phase 7 Completion

| File | Action | Reason |
|---|---|---|
| `.github/workflows/ci-tests.yml` | Replace | Split into `ci-acceptance-smoke.yml` + `ci-acceptance-full.yml` |
| `Makefile` target `test-acceptance` | Update | Point to `pytest tests/acceptance/ -m smoke` |

---

## Appendix A: Directory Structure After Implementation

```
tests/acceptance/
├── __init__.py
├── conftest.py
├── runtime.py                         # NEW: ObservabilityStack class
├── requirements.txt                   # NEW: Python dependencies
├── features/
│   ├── otel_pipeline.feature          # PHASE 1: 3 @smoke scenarios
│   ├── loki_logs.feature              # PHASE 1: 3 @smoke scenarios
│   ├── alertmanager.feature           # PHASE 1: 2 @smoke scenarios
│   ├── dashboards.feature             # PHASE 1: 2 @smoke scenarios
│   ├── multi_plane_contract.feature   # PHASE 2: 4 @smoke @contract scenarios
│   ├── slo_gates.feature              # PHASE 3: 6 @full scenarios
│   └── chaos_resilience.feature       # PHASE 5: 5 @chaos scenarios
├── steps/
│   ├── __init__.py
│   ├── shared_steps.py                # PHASE 1: Common step definitions
│   ├── otel_steps.py                  # PHASE 1: OTel pipeline steps
│   ├── loki_steps.py                  # PHASE 1: Loki steps
│   ├── alertmanager_steps.py          # PHASE 1: Alertmanager steps
│   ├── dashboard_steps.py             # PHASE 1: Dashboard steps
│   ├── multi_plane_steps.py           # PHASE 2: Contract test steps
│   ├── slo_steps.py                   # PHASE 3: SLO measurement steps
│   └── chaos_steps.py                 # PHASE 5: Chaos injection steps
├── workloads/
│   ├── __init__.py                    # PHASE 4: Workload registry
│   ├── web_api.py                     # PHASE 4: Web app simulation
│   ├── batch_job.py                   # PHASE 4: Batch job simulation
│   ├── log_emitter.py                 # PHASE 4: Log generator
│   └── dora_events.py                 # PHASE 4: DORA event generator
├── evidence/
│   ├── __init__.py
│   ├── collector.py                   # PHASE 6: Evidence collection
│   ├── generate_runbook.py            # PHASE 6: Runbook snippet generator
│   └── slo_report.py                  # PHASE 6: SLO report generator
└── observability-pipeline/            # PHASE 1: Removed (legacy)
    ├── test-otel-pipeline.sh          │   (removed after migration)
    ├── test-loki-logs.sh              │
    ├── test-alertmanager.sh           │
    ├── test-dashboard-validation.sh   │
    └── reports/                       │   (kept for historical reference)

.github/workflows/
├── ci-pipeline.yml                    # UPDATED: points to ci-acceptance-smoke.yml
├── ci-acceptance-smoke.yml            # NEW: Pre-merge smoke tests
├── ci-acceptance-full.yml             # NEW: Post-merge full acceptance
├── ci-chaos-nightly.yml               # NEW: Nightly chaos tests
├── deploy.yml                         # UPDATED: depends on full acceptance
├── ci-tests.yml                       # PHASE 7: Removed (replaced)
└── ci-quality.yml                     # Unchanged
```

---

## Appendix B: Implementation Order & Dependencies

```
Phase 1 ───────────────────────────────────────────────┐
  ├── runtime.py                           ────────────┤
  ├── conftest.py (fixtures, markers)      ────────────┤
  ├── features/*.feature (smoke)           ────────────┤
  ├── steps/*.py                           ────────────┤
  └── Shell script deprecation                         │
                                                       ▼
Phase 2 ─────────────────────────── needs: runtime.py ─┤
  ├── multi_plane_contract.feature                      │
  ├── multi_plane_steps.py                              │
  └── Cross-plane test container                        │
                                                       ▼
Phase 3 ─────────────────── needs: runtime.py + Phase 2 ┤
  ├── slo_gates.feature                                 │
  ├── slo_steps.py                                      │
  └── SLO report generator                              │
                                                       ▼
Phase 4 ────────── needs: runtime.py (independent path) │
  ├── workloads/*.py                                     │
  └── Used by Phase 2, 3, 5                              │
                                                       ▼
Phase 5 ───────── needs: runtime.py + Phase 4 ──────────┤
  ├── chaos_resilience.feature                           │
  ├── chaos_steps.py                                     │
  └── Chaos evidence generator                           │
                                                       ▼
Phase 6 ───────── needs: runtime.py (independent path) ─┤
  ├── evidence/collector.py                              │
  ├── evidence/generate_runbook.py                       │
  └── evidence/slo_report.py                             │
                                                       ▼
Phase 7 ───────── needs: Phase 1-6 complete ────────────┤
  ├── ci-acceptance-smoke.yml
  ├── ci-acceptance-full.yml
  ├── ci-chaos-nightly.yml
  └── Pipeline integration
```

---

## Appendix C: Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Shell→pytest migration introduces regressions** | Medium | High | Run shell and pytest in parallel for 1 sprint. Compare results before removing shells. |
| **SLO tests flake due to timing** | High | Medium | Use retry-with-backoff patterns. Allow 2σ tolerance before failing. Track flake rate. |
| **Chaos tests destabilize CI environment** | Low | High | Run chaos on dedicated schedule (nightly), not in CI. Use `if: always()` cleanup. |
| **Post-merge acceptance adds deploy latency** | Medium | Medium | Run acceptance in parallel with deploy. Gate on health check, not test completion. |
| **Evidence pipeline adds complexity** | Low | Low | Start simple: capture JSON files to directory. Only add processing when value is proven. |
| **Workload generators conflict with real telemetry** | Low | Low | Use unique label namespacing (`test_run_id`) on all synthetic telemetry. |

---

*This plan is a living document. Update it as phases are completed and new insights emerge.*
