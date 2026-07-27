# Phase 5: Chaos & Failure Injection — Design

**Version:** 1.0.0
**Date:** 2026-06-29
**Depends on:** specification.md (Phase 5), Phase 1 (ObservabilityStack), Phase 4 (Workload Generators)

---

## 1. Architecture Overview

Phase 5 adds chaos resilience testing to the existing acceptance test framework. It leverages:
- **Phase 1:** `ObservabilityStack` runtime for service lifecycle management
- **Phase 4:** Synthetic workload generators (`web_api`, `log_emitter`) for continuous telemetry
- **Existing:** `tests/acceptance/evidence/chaos_report.py` for evidence generation

### Test Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     NIGHTLY CHAOS TEST RUN                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Start core stack (ObservabilityStack.start())                  │
│  2. Start synthetic workload (Phase 4 workload generator)          │
│  3. Wait for steady state (30s)                                     │
│  4. FOR EACH chaos scenario:                                        │
│     a. Inject failure (stop service, disconnect network, etc.)     │
│     b. Observe behavior (buffering, errors, health)                │
│     c. Restore service                                              │
│     d. Measure recovery time and data loss                         │
│     e. Capture events for evidence                                 │
│  5. Generate chaos report (Mermaid + Markdown)                     │
│  6. Cleanup (ObservabilityStack.stop())                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Chaos Step Implementations (`tests/acceptance/steps/chaos_steps.py`)

Each Gherkin step maps to a Python function that:
1. Executes the failure injection via Docker Compose CLI
2. Validates expected behavior during failure
3. Restores the service
4. Measures recovery metrics
5. Records events for evidence generation

#### Key Implementation Details

| Step | Method | Verification |
|------|--------|--------------|
| `stop_service` | `docker compose stop <service>` | Service state = "exited" |
| `start_service_after_delay` | `docker compose up -d <service>` | Service state = "running", health check passes |
| `disconnect_from_network` | `docker network disconnect observability-lab <container>` | Container removed from network |
| `reconnect_to_network_after_delay` | `docker network connect observability-lab <container>` | Container rejoined network |

### 2.2 Synthetic Workload Integration

Phase 4 workload generator runs continuously during chaos tests:

```python
# Started before chaos scenarios
workload = get_workload("web_api", otlp_endpoint="http://localhost:4318")
workload.start_continuous(rate_per_second=5)  # 5 traces/sec

# During chaos: workload keeps sending
# After recovery: verify traces appear in Tempo
```

### 2.3 Evidence Collection

Events recorded during each scenario:
- `failure_start`: When failure injected
- `failure_end`: When service stopped/disconnected confirmed
- `recovery_start`: When restore initiated
- `recovery_end`: When all pipelines healthy
- `metric`: Measurements (latency, data loss, gap duration)

---

## 3. Chaos Scenarios Implementation

### 3.1 OBS-CHAOS-001: Log Pipeline Survives Loki Restart

**Failure Injection:** `docker compose stop loki`
**Expected Behavior:**
- Alloy continues running (process state = running)
- Alloy buffers logs in memory/file buffer
- After `docker compose up -d loki`, logs replay within 60s
- Log count matches pre-restart count (±5%)

**Verification Steps:**
1. Query Loki for baseline log count before stop
2. Stop Loki
3. Verify Alloy still running (`docker compose ps alloy`)
4. Start Loki after 30s
5. Poll Loki until log streams return
6. Compare log counts

### 3.2 OBS-CHAOS-002: Metrics Pipeline Survives Prometheus Restart

**Failure Injection:** `docker compose stop prometheus`
**Expected Behavior:**
- Existing metrics queryable via Grafana (cached)
- OTel Collector buffers metrics (Prometheus remote_write queue)
- After restart, Prometheus scrapes all targets within 60s
- Metric gaps ≤ 90s

**Verification Steps:**
1. Query Prometheus `up` metric for baseline
2. Stop Prometheus
3. Verify Grafana still serves dashboards
4. Start Prometheus after 30s
5. Poll `up` metric until all targets UP
6. Check `scrape_duration_seconds` for gaps

### 3.3 OBS-CHAOS-003: OTel Collector Restart Transparency

**Failure Injection:** `docker compose restart otel-collector`
**Expected Behavior:**
- Trace pipeline resumes within 30s
- New traces queryable in Tempo within 30s of restart
- Exporters retry with exponential backoff

**Verification Steps:**
1. Generate baseline trace, verify in Tempo
2. Restart OTel Collector
3. Poll Tempo `/ready` endpoint
4. Generate new trace after restart
5. Verify new trace appears in Tempo

### 3.4 OBS-CHAOS-004: Network Partition Self-Heals

**Failure Injection:** `docker network disconnect observability-lab <otel-container>`
**Expected Behavior:**
- OTel Collector logs connection errors (not crash)
- Exporters enter backoff state
- After reconnect, all pipelines resume within 30s

**Verification Steps:**
1. Get OTel Collector container ID
2. Disconnect from `observability-lab` network
3. Verify OTel Collector still running (check logs for errors)
4. Reconnect after 20s
5. Verify Prometheus, Loki, Tempo all queryable

### 3.5 OBS-CHAOS-005: Grafana Datasource Removal Fails Gracefully

**Failure Injection:** Remove datasource provisioning file
**Expected Behavior:**
- Grafana continues serving cached dashboards
- New queries fail with appropriate error (not crash)

**Verification Steps:**
1. Verify Grafana dashboards accessible
2. Remove a datasource YAML from provisioning
3. Reload Grafana provisioning (or restart Grafana)
4. Verify dashboards still load (cached)
5. Execute query against removed datasource → graceful error

---

## 4. Data Structures

### 4.1 ChaosEvent (from `chaos_report.py`)

```python
@dataclass
class ChaosEvent:
    timestamp: str          # ISO 8601 UTC
    event_type: str         # failure_start|failure_end|recovery_start|recovery_end|metric
    service: str            # loki|prometheus|otel-collector|tempo|grafana|alloy
    description: str        # Human-readable
    metadata: dict          # duration_ms, data_loss_pct, gap_seconds, etc.
```

### 4.2 ChaosReportGenerator (from `chaos_report.py`)

Outputs:
- **Mermaid sequence diagram** → `reports/chaos-evidence/chaos-timeline.mmd`
- **Markdown report** → `reports/chaos-report.md`
- **JSON evidence** → `reports/chaos-evidence/chaos-events.json`

---

## 5. CI/CD Integration

### 5.1 Nightly Workflow (`.github/workflows/ci-chaos-nightly.yml`)

```yaml
name: Chaos Nightly
on:
  schedule:
    - cron: "0 2 * * *"  # 2am daily
jobs:
  chaos-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - checkout
      - setup-python
      - install-deps
      - start-stack
      - run-chaos: pytest tests/acceptance/ -m chaos -v
      - generate-report
      - upload-evidence
      - cleanup
```

### 5.2 Test Markers

```python
# conftest.py
# @chaos  → runs nightly only (not in pre-merge or post-merge)
```

---

## 6. Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `ObservabilityStack` | Phase 1 (`tests/acceptance/runtime.py`) | Stack lifecycle, typed clients |
| `get_workload()` | Phase 4 (`tests/acceptance/workloads/__init__.py`) | Synthetic telemetry generation |
| `ChaosReportGenerator` | Existing (`tests/acceptance/evidence/chaos_report.py`) | Evidence generation |
| Docker Compose CLI | System | Service control, network manipulation |

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Chaos tests leave stack in broken state | Medium | High | `try/finally` cleanup in conftest; `if: always()` in CI |
| Flaky timing (recovery takes longer) | High | Medium | Generous timeouts; retry with backoff; track flake rate |
| Synthetic workload interferes with real metrics | Low | Low | Unique `test_run_id` label on all synthetic telemetry |
| Network disconnect affects other tests | Low | High | Run chaos in isolation (nightly); dedicated CI runner |
