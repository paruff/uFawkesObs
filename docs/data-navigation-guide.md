# Observability Data Navigation Guide

## Quick Summary: Where Your Data Is

| Data Type   | Storage      | Status         | View In Grafana        |
| ----------- | ------------ | -------------- | ---------------------- |
| **Metrics** | Prometheus   | ✅ **Active**  | Explore → Prometheus   |
| **Logs**    | Loki         | ⚠️ **Limited** | Explore → Loki         |
| **Traces**  | Tempo        | ⚠️ **Not Yet** | Explore → Tempo        |
| **Alerts**  | Alertmanager | ✅ **Active**  | Alerting → Alert Rules |

---

## 1. METRICS (Prometheus) ✅

### What's Being Collected

Your observability stack is actively collecting **internal infrastructure metrics**:

```
uFawkesObs Stack Metrics:
├─ Prometheus (self-monitoring)
│  ├─ prometheus_tsdb_symbol_table_size_bytes
│  ├─ prometheus_tsdb_data_compaction_duration_seconds
│  └─ prometheus_sd_discovered_targets
├─ OpenTelemetry Collector
│  ├─ otelcol_exporter_queue_size
│  ├─ otelcol_http_server_duration
│  └─ otelcol_receiver_accepted_spans
├─ Alertmanager
│  ├─ alertmanager_alerts
│  ├─ alertmanager_notifications_total
│  └─ alertmanager_config_last_reload_successful
└─ Loki/Tempo/Grafana (system metrics)
```

### How to View Metrics in Grafana

**Method 1: Pre-made Dashboards**

1. Open http://localhost:3000
2. Left sidebar → **Dashboards**
3. Select one of:
   - **"Observability Stack Health"** ← START HERE (shows collector & infrastructure)
   - **"Prometheus"** (Prometheus internal metrics)
   - **"OTel Collector"** (collector performance)
   - **"Infrastructure Overview"** (system-level metrics)

**Method 2: Ad-hoc Exploration**

1. Open http://localhost:3000
2. Left sidebar → **Explore**
3. Top left dropdown → Select **"Prometheus"**
4. In query box, try:
   ```
   up{job="prometheus"}
   ```
5. Or search available metrics:
   ```
   up
   ```
   This shows which targets are running.

**Available Prometheus Queries**

```promql
# Infrastructure health
up{job="prometheus"}                          # Prometheus itself
up{job="otel-collector"}                      # OTel Collector
up{job="alertmanager"}                        # Alertmanager
up{job="otel-app-metrics"}                    # App metrics via OTel

# OTel Collector internals
rate(otelcol_exporter_queue_size[5m])         # Queue depth over time
otelcol_http_server_duration_count            # HTTP request count
increase(otelcol_exporter_sent_spans[5m])     # Spans sent to exporters

# Prometheus internals
prometheus_tsdb_symbol_table_size_bytes       # Database size
prometheus_sd_discovered_targets              # Service discovery targets
```

---

## 2. LOGS (Loki) ✅ Active

### Current Status: Running

Loki receives container logs from **Grafana Alloy**, which automatically discovers and
scrapes all Docker container stdout/stderr logs via the Docker socket.

### Viewing Logs in Grafana

1. http://localhost:3000
2. Left sidebar → **Explore**
3. Top left dropdown → **"Loki"**
4. Try queries like:
   ```
   {job="docker"}                      # All container logs
   {compose_service="grafana"}         # Specific service
   {compose_project="ufawkesobs"} # All uFawkesObs containers
   ```

---

## 3. TRACES (Tempo) ✅

### Current Status: Active

The `apps` profile's `telemetry-generator` demo app (Python/Flask) is fully
instrumented with the OpenTelemetry SDK and exports spans via OTLP to the
collector — see `apps/telemetry-generator/README.md`. Start it with
`make up-apps`.

### Instrumenting Your Own App

1. **OpenTelemetry SDK for your language** installed
2. **Instrumentation code** pointed at the collector, e.g. (Python):

   ```python
   from opentelemetry import trace
   from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

   exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces")
   tracer = trace.get_tracer("your-app")

   with tracer.start_as_current_span("process_request"):
       ...
   ```

3. See [Multi-Stack Integration](multi-stack-integration.md) for connecting
   an external app's compose stack to this network.

### How to View Traces

1. http://localhost:3000
2. Left sidebar → **Explore**
3. Top left dropdown → **"Tempo"**
4. Click "Search" button (top right)
5. Will show traces by:
   - Service name (e.g. `telemetry-generator`, or your app's service name)
   - Operation name
   - Duration
   - Status

---

## 4. ALERTS (Alertmanager) ✅

### Current Status: Active

Pre-configured alert rules are in place.

### Viewing Alerts in Grafana

1. http://localhost:3000
2. Left sidebar → **Alerting** → **Alert rules**
3. Shows current alert status
4. Check `config/prometheus/alerts.yml` for rule definitions

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   OBSTACKD STACK                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────────┐        │
│  │   Prometheus │◄────────┤  OTel Collector  │        │
│  │  (Metrics)   │         │  (Telemetry)     │        │
│  └──────────────┘         └──────────────────┘        │
│         ▲                           ▲                  │
│         │                           │                  │
│         └───────────┬───────────────┘                  │
│                     │                                  │
│              Scrapes every 15s                         │
│                                                         │
│  ┌──────────────┐    ┌──────────┐    ┌──────────┐    │
│  │    Loki      │    │  Tempo   │    │ Grafana  │    │
│  │   (Logs)     │    │ (Traces) │    │  (UI)    │    │
│  └──────────────┘    └──────────┘    └──────────┘    │
│         ▲                 ▲                            │
│         │                 │                            │
│         └────────┬────────┘                            │
│                  │                                     │
│           Receives via OTLP                            │
│           (from OTel Collector)                        │
│                                                        │
└─────────────────────────────────────────────────────────┘
                      ▲
                      │ observability-lab network
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼──────┐          ┌──────▼────┐
    │   YOUR    │          │   OTHER   │
    │    APP    │          │   APPS    │
    │   STACK   │          │   STACK   │
    └───────────┘          └───────────┘
```

---

## What to Look At First

### 1. **Observability Stack Health Dashboard** (START HERE)

This shows the health of uFawkesObs itself:

```
✓ Click: Dashboards → Observability Stack Health
Shows:
- OTel Collector status
- Receiver metrics
- Exporter metrics
- Memory usage
- Uptime
```

### 2. **Prometheus Targets**

Verify what's being scraped:

```
In Grafana:
✓ Menu → Configuration → Data sources → Prometheus
✓ Click "Explore"
✓ Query: up
Should show 4 targets UP:
- prometheus (self)
- otel-collector (metrics)
- alertmanager
- otel-app-metrics
```

### 3. **Metric Explorer**

Try these to understand available data:

```promql
# Show all metric names
{__name__=~".+"}

# OTel Collector workload
rate(otelcol_exporter_queue_size[5m])
otelcol_http_server_duration_count

# System health
up{job=~"prometheus|alertmanager|otel-collector"}

# Container info
count(up) by (job)
```

---

## Troubleshooting: "Why don't I see X?"

### "No Logs in Loki"

- **Root cause**: Alloy not running or not connected to Docker socket
- **Fix**: Check `docker compose logs alloy` and `curl http://localhost:12345/metrics`
- **Verification**:
  ```bash
  curl http://localhost:3100/loki/api/v1/label/job/values
  # Should return ["docker"]
  ```

### "No Traces in Tempo"

- **Root cause**: your app doesn't have OTel SDK instrumentation (the `apps`
  profile's `telemetry-generator` demo app does, and traces from it should
  already appear — see `apps/telemetry-generator/README.md`)
- **Fix**: add OpenTelemetry instrumentation to your app, or run
  `make up-apps` to generate traces from the demo app instead
- **Verification**:
  ```bash
  curl http://localhost:3200/api/traces
  # Should return traces once an instrumented app is running
  ```

### "Metrics Missing from Prometheus"

- **Root cause**: Target not in scrape config
- **Fix**: Add to `config/prometheus/prometheus.yaml`
- **Verification**:
  ```bash
  curl 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets'
  ```

### "Grafana Shows Empty Dashboards"

- **Root cause**: Dashboard queries don't match available metrics
- **Fix**:
  1. Go to Explore
  2. Try a simple query like `up`
  3. Edit dashboard panels to use correct metric names
- **Verification**:
  ```bash
  curl 'http://localhost:9090/api/v1/labels' | jq '.data | length'
  # Should show > 40
  ```

---

## Quick API Tests

### Test Prometheus

```bash
curl 'http://localhost:9090/api/v1/targets'
curl 'http://localhost:9090/api/v1/labels'
curl 'http://localhost:9090/api/v1/query?query=up'
```

### Test Loki

```bash
curl 'http://localhost:3100/loki/api/v1/labels'
curl 'http://localhost:3100/loki/api/v1/label/job/values'
```

### Test Tempo

```bash
curl 'http://localhost:3200/api/traces'
curl 'http://localhost:3200/api/search'
```

### Test OTel Collector Metrics

```bash
curl 'http://localhost:8888/metrics' | grep -i otelcol
curl 'http://localhost:8889/metrics' | head -20
```

---

## Summary Table

| Component      | URL                          | Data                   | Action                          |
| -------------- | ---------------------------- | ---------------------- | ------------------------------- |
| Prometheus     | `http://localhost:9090`      | Infrastructure metrics | ✅ Viewing now                  |
| Grafana        | `http://localhost:3000`      | Dashboards             | ✅ Use this                     |
| Loki           | `http://localhost:3100`      | Logs                   | ✅ Alloy collecting Docker logs |
| Tempo          | `http://localhost:3200`      | Traces                 | ✅ telemetry-generator instrumented |
| OTel Collector | `http://localhost:4317/4318` | OTLP receiver          | ✅ Ready for data               |
| Alertmanager   | `http://localhost:9093`      | Alerts                 | ✅ Configured                   |
