---
name: otel-collector
description: OpenTelemetry Collector configuration rules for uFawkesObs. Covers pipeline anatomy, common wiring errors, and the specific constraints of the Docker Compose deployment.
license: MIT
compatibility: opencode
---

# Skill: otel-collector

## Purpose

OpenTelemetry Collector configuration rules for uFawkesObs. Covers pipeline anatomy, common wiring errors, and the specific constraints of the uFawkesObs Docker Compose deployment.

Load this skill before editing `config/otel/collector.yaml`.

---

## Pipeline anatomy

The OTel Collector config has four top-level sections. All must be consistent with each other.

```yaml
receivers: # Where data comes in
processors: # Transform, filter, batch
exporters: # Where data goes out
service:
  pipelines: # Wire receivers → processors → exporters
    traces: ...
    metrics: ...
    logs: ...
```

**Critical rule:** A component defined in `receivers`, `processors`, or `exporters` that is NOT referenced in `service.pipelines` is silently ignored. This is the most common agent error with OTel config.

---

## uFawkesObs pipeline map

```
OTLP receiver (gRPC :4317, HTTP :4318)
      │
      ├──► traces ──► memory_limiter ──► batch ──► otlp/tempo (tempo:4317)
      │                                                  └──► debug (console)
      │
      ├──► metrics ──► memory_limiter ──► batch ──► prometheus (:8889)
      │                                                  └──► debug (console)
      │
      ├──► metrics/ai ──► memory_limiter ──► filter/ai ──► attributes/ai ──► batch ──► prometheus (:8889)
      │   (gen_ai.* metrics only)
      │
      └──► logs ────► memory_limiter ──► batch ──► loki (loki:3100)
                                                     └──► debug (console)

Self-telemetry:
  Collector emits its own metrics at :8888
  Prometheus scrapes :8888 directly
```

---

## Exporter endpoint rules

### Never use localhost

In Docker Compose, `localhost` in an exporter target resolves to the OTel Collector container itself, not the target service.

```yaml
# CORRECT — Docker Compose service name
exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true # Required for plain gRPC without TLS

  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: app_metrics
    const_labels:
      service: otel-collector

  loki:
    endpoint: http://loki:3100/loki/api/v1/push
```

### TLS for gRPC exporters

Any `otlp` exporter using gRPC without TLS certificates must include:

```yaml
tls:
  insecure: true
```

Without this, the connection fails silently on startup in many versions.

---

## Receiver configuration

### OTLP receiver — standard for uFawkesObs

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
```

`0.0.0.0` binds to all interfaces in the container. This is correct — port exposure to the host is controlled by `compose.yaml`, not by the receiver bind address.

### Prometheus receiver — for scraping other services

```yaml
receivers:
  prometheus:
    config:
      scrape_configs:
        - job_name: "otel-collector"
          static_configs:
            - targets: ["localhost:8888"] # Exception: localhost IS correct here
```

`localhost:8888` is correct inside the collector container when scraping its own self-telemetry endpoint. This is the only valid localhost reference.

---

## Processor configuration

### batch processor — always include

```yaml
processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
```

Without batching, the collector sends one telemetry item per request, overwhelming exporters under load.

### memory_limiter — recommended for stability

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128
```

If present, `memory_limiter` must be the FIRST processor in every pipeline.

---

## AI pipeline (`metrics/ai`)

The AI pipeline filters `gen_ai.*` metrics from all OTLP telemetry and routes them through
dedicated processors. It uses a **separate named pipeline** from the default `metrics` pipeline
to avoid risking existing metric scraping.

### Processors

```yaml
processors:
  filter/ai:                    # Passes only AI-related metric names
    error_mode: ignore
    metrics:
      include:
        match_type: regexp
        metric_names:
          - "gen_ai\\..*"
          - "llm\\..*"
          - "openllmetry\\..*"
          - "ai\\..*"

  attributes/ai:                # Enriches AI metrics with environment labels
    actions:
      - key: ai.environment
        value: development
        action: insert
      - key: ai.platform
        value: fawkes-idp
        action: insert
```

### Pipeline wiring

```yaml
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, debug]

    metrics/ai:              # Separate pipeline — do not merge with metrics
      receivers: [otlp]
      processors: [memory_limiter, filter/ai, attributes/ai, batch]
      exporters: [prometheus]
```

### Rules

- `filter/ai` uses `error_mode: ignore` — if a metric name pattern fails, the pipeline
  continues without dropping data
- `memory_limiter` must always be the **first** processor, even in the AI pipeline
- `attributes/ai` inserts `ai.environment` and `ai.platform` labels on every AI metric
- The `prometheus` exporter on port 8889 (shared with the default `metrics` pipeline)
- Never add AI-specific processors to the default `metrics` pipeline — filter/ai would
  drop infrastructure metrics

---

## Validation

```bash
# Syntax check (does not require running services)
docker compose config

# Check collector is accepting and exporting
curl http://localhost:8888/metrics | grep otelcol_exporter_sent_spans

# Check app metrics endpoint
curl http://localhost:8889/metrics
```

Expected after healthy startup:

- `otelcol_receiver_accepted_spans_total` — increasing
- `otelcol_exporter_sent_spans_total` — increasing (if traces are flowing)
- `otelcol_process_uptime` — present

---

## Common failure modes

| Symptom                                               | Cause                                             | Fix                                        |
| ----------------------------------------------------- | ------------------------------------------------- | ------------------------------------------ |
| Exporter defined but no data sent                     | Not wired in service.pipelines                    | Add to the correct pipeline                |
| `connection refused` to tempo:4317                    | `tls.insecure: true` missing                      | Add TLS block                              |
| Metrics reach Prometheus but traces don't reach Tempo | otlp/tempo exporter missing from traces pipeline  | Check service.pipelines.traces.exporters   |
| Self-telemetry at :8888 works but :8889 is empty      | prometheus exporter not wired in metrics pipeline | Add to service.pipelines.metrics.exporters |
