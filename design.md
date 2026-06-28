# Design — OBS-AI-01: Add AI Metrics Pipeline to OTel Collector Config

**Specification:** specification.md (OBS-AI-01)

---

## Impacted Components

| Component | File | Change Type |
|---|---|---|
| OTel Collector config | `config/otel/collector.yaml` | Add processors + pipeline |
| Unit tests | `tests/unit/test_otel_config_validation.py` | Add test class |

No other components are impacted. No changes to `compose.yaml`, no new services, no new receivers or exporters.

---

## Technical Approach

### Current State

The OTel Collector config (`config/otel/collector.yaml`) has three pipelines:

```yaml
service:
  pipelines:
    metrics:   # receivers: [otlp], processors: [memory_limiter, batch], exporters: [prometheus, debug]
    traces:    # receivers: [otlp], processors: [memory_limiter, batch], exporters: [otlp/tempo, debug]
    logs:      # receivers: [otlp], processors: [memory_limiter, batch], exporters: [loki, debug]
```

### Target State

Add a fourth pipeline `metrics/ai` with two new processors:

```yaml
processors:
  # ... existing memory_limiter and batch ...

  filter/ai:
    error_mode: ignore
    metrics:
      include:
        match_type: regexp
        metric_names:
          - "gen_ai\\..*"
          - "llm\\..*"
          - "openllmetry\\..*"
          - "ai\\..*"

  attributes/ai:
    actions:
      - key: ai.environment
        value: development
        action: insert
      - key: ai.platform
        value: fawkes-idp
        action: insert

service:
  pipelines:
    # ... existing metrics, traces, logs UNCHANGED ...
    metrics/ai:
      receivers: [otlp]
      processors: [memory_limiter, filter/ai, attributes/ai, batch]
      exporters: [prometheus]
```

### Design Decisions

1. **Separate named pipeline, not merged into `metrics`:** The `otel-collector` skill explicitly states "Never add AI-specific processors to the default metrics pipeline — this risks breaking existing Prometheus scraping." A separate `metrics/ai` pipeline isolates AI processing.

2. **Reuses existing `otlp` receiver and `prometheus` exporter:** AI SDKs send standard OTLP. No new receivers needed. The `prometheus` exporter on port 8889 already exposes metrics for Prometheus to scrape. Using it means no changes to `compose.yaml` ports or Prometheus scrape config.

3. **`error_mode: ignore` on filter/ai:** If no AI metrics arrive (e.g. before AI tooling is integrated), the filter processor silently passes nothing through instead of erroring. This prevents the collector from crashing when no AI instrumentation exists.

4. **`action: insert` on attributes:** Uses `insert` (not `upsert`) so that if the attribute already exists on the metric (set by the emitting SDK), it won't be overwritten. The processor only adds defaults when they're missing.

5. **Processor ordering `[memory_limiter, filter/ai, attributes/ai, batch]`:** Per OTel best practice, `memory_limiter` must be first. `filter/ai` runs before `attributes/ai` so we only tag metrics that pass the filter. `batch` is last for efficiency.

6. **No `debug` exporter on `metrics/ai`:** The existing pipelines include `debug` exporter for development visibility. For the AI pipeline, we omit `debug` to avoid flooding logs with AI metric data during normal operation. Debug can be added ad-hoc if needed.

### Exporter Choice — `prometheus` not `prometheusremotewrite`

The issue body says "exports to existing `prometheus` exporter (port 8889)". The current `metrics` pipeline already uses the `prometheus` exporter (port 8889). This is the correct choice because:
- The `prometheus` exporter makes metrics available at `:8889/metrics` for Prometheus to scrape
- The `otlp-collector` skill recommends using `prometheusremotewrite/ai` with a separate endpoint
- However, the `prometheus` exporter already works and is simpler — no additional Prometheus remote-write config needed
- The existing Prometheus scrape config already targets `otel-collector:8889`
- Both `metrics` and `metrics/ai` pipelines publishing to the same `:8889` endpoint works — the exporter merges metrics from all pipelines that reference it

---

## Constraints

- **OTel Collector version:** v0.120.0 (already deployed, supports `filter` and `attributes` processors)
- **No compose.yaml changes:** The `prometheus` exporter on port 8889 is already exposed
- **No new receivers:** AI SDKs send standard OTLP to `:4317/:4318`
- **No new exporters:** Reuses the existing `prometheus` exporter
- **Backward compatibility:** Existing pipelines must remain unchanged
