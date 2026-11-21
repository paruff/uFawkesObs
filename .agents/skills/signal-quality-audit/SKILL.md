---
name: signal-quality-audit
description: "Silent-data-loss checklist for uFawkesObs: a config that validates but whose signal never arrives. Use when reviewing a change to the Collector, Loki, Tempo or Prometheus config, or when data is missing from a dashboard."
license: MIT
compatibility: opencode
---

# Skill: signal-quality-audit

Checks for signal that is accepted and then lost. Component syntax belongs to
`otel-collector`; ports and versions to `obs-stack`. Prove arrival with
`make smoke-telemetry`; `make lint-config` only proves the config parses.

## Checklist

1. **Processor order.** In every pipeline in `config/otel/collector.yaml`,
   `memory_limiter` is first and `batch` is last (today:
   `[memory_limiter, batch]`; `metrics/ai` adds `filter/ai`, `attributes/ai`
   between them).
2. **Attributes survive.** After any processor change, check the attribute you
   care about still reaches the backend; `attributes/ai` and `filter/ai`
   rewrite or drop data. Round-trip it, do not trust the diff.
3. **Sampler is deliberate.** There is no sampler today, so every trace is
   kept. Adding `probabilistic_sampler` or `tail_sampling` is a decision to
   record, not a default.
4. **Metric cardinality is bounded.** The `prometheus` exporter on :8889 turns
   every attribute into a label, with `metric_expiration: 5m`. Never put ids,
   user input or timestamps in metric attributes. Tempo `span_metrics`
   `dimensions` is `[]`; adding to it multiplies series.
5. **Logs are parsed, not just stored.** Loki receives OTLP natively
   (`otlphttp/loki`). A label that is not indexed is only filterable by
   scanning. Confirm the label you query is a stream label or structured
   metadata, and that `service_name` is set by the sender.
6. **Loki limits.** `limits_config` (`ingestion_rate_mb`,
   `reject_old_samples_max_age`) rejects data silently to the sender; watch
   `loki_discarded_samples_total`.

## Counters that show loss (Collector :8888, `otelcol_` prefix)

| Question | Metrics |
|---|---|
| Receiver refused data? | `otelcol_receiver_refused_{spans,metric_points,log_records}` |
| Exporter failed? | `otelcol_exporter_send_failed_*` |
| Queue full? | `otelcol_exporter_queue_size` vs `otelcol_exporter_queue_capacity` |
| memory_limiter refusing? | `otelcol_processor_memory_limiter_refused_*` (compare `_accepted_*`); 0.162 has no `processor_dropped_*` |

Existing alert: `UFawkesObsOtelCollectorDropped` covers dropped, refused and
failed-export items for all three signals. Loki: `UFawkesObsLokiIngestionDropped`.
