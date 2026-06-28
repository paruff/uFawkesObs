# AI Observability Guide

> How uFawkesObs monitors AI model performance, LLM latency, token consumption, and
> suggestion acceptance rates using OpenTelemetry, Prometheus, and Grafana.

---

## Overview

uFawkesObs provides an end-to-end AI observability pipeline consisting of three layers:

| Layer | Component | What It Does |
|---|---|---|
| **Collection** | OTel Collector `metrics/ai` pipeline | Filters `gen_ai.*` metrics from application telemetry, enriches with AI environment labels |
| **Aggregation** | Prometheus AI recording and alert rules | Computes latency P99/P50, token rates, acceptance rates; fires alerts at DORA 2025 thresholds |
| **Visualisation** | Grafana AI Capabilities dashboard | 9-panel dashboard showing real-time AI performance with DORA performance bands |

Together these layers implement the four AI capabilities metrics defined by the DORA 2025 report.

---

## Architecture

```
┌───────────────────────────────────────────────┐
│  Application / AI SDK                         │
│  Emits gen_ai.* OTLP metrics on :4317/:4318   │
│  (e.g. gen_ai.client.operation.duration)      │
└──────────────────┬────────────────────────────┘
                   │ OTLP gRPC/HTTP
                   ▼
┌───────────────────────────────────────────────┐
│  OTel Collector (metrics/ai pipeline)          │
│                                                │
│  1. memory_limiter — prevents OOM              │
│  2. filter/ai — passes only gen_ai.*,          │
│     llm.*, openllmetry.*, ai.* metrics        │
│  3. attributes/ai — inserts                    │
│     ai.environment=development                 │
│     ai.platform=fawkes-idp                     │
│  4. batch — groups for efficiency              │
│                                                │
│  Exports to Prometheus at :8889                │
└──────────────────┬────────────────────────────┘
                   │ Prometheus scrape (app_metrics namespace)
                   ▼
┌───────────────────────────────────────────────┐
│  Prometheus                                    │
│                                                │
│  Recording rules (ai-rules.yml):               │
│  • ai:llm_request_latency_p99:seconds         │
│  • ai:llm_request_latency_p50:seconds         │
│  • ai:token_usage_rate:per_minute              │
│  • ai:suggestion_acceptance_rate:ratio         │
│                                                │
│  Alert rules (ai-rules.yml):                   │
│  • AILLMLatencyHigh — P99 > 10s               │
│  • AIReworkRateHigh — rework > 10%             │
│  • AIReworkRateCritical — rework > 20%         │
│  • AITokenBudgetHigh — tokens > 100K/min       │
└──────────────────┬────────────────────────────┘
                   │ PromQL queries
                   ▼
┌───────────────────────────────────────────────┐
│  Grafana AI Capabilities Dashboard             │
│  dashboards/platform/ai-capabilities.json      │
│                                                │
│  • P99 Latency (stat + timeseries)             │
│  • Token Usage Rate (stat + timeseries)        │
│  • Suggestion Acceptance Rate (stat + trend)   │
│  • AI Rework Rate (stat + trend)               │
│  • AI Active Alerts list                       │
└───────────────────────────────────────────────┘
```

---

## Metrics Reference

### Raw OTel Metrics (gen_ai.* namespace)

These metrics are emitted by AI SDKs (OpenTelemetry-instrumented) and flow through the
`metrics/ai` pipeline. OTel metric names with `.` are converted to `_` in Prometheus.

| OTel Metric | Prometheus Metric | Type | Description |
|---|---|---|---|
| `gen_ai.client.operation.duration` | `gen_ai_client_operation_duration_bucket` | Histogram | LLM request latency distribution |
| `gen_ai.client.token.usage` | `gen_ai_client_token_usage_sum`/`_count` | Counter | Token consumption count |
| `gen_ai.client.request.duration` (future) | `gen_ai_client_request_duration_*` | Histogram | End-to-end request duration |
| `gen_ai.suggestion.accepted` (future) | `gen_ai_suggestion_accepted_total` | Counter | Count of accepted AI suggestions |
| `gen_ai.suggestion.total` (future) | `gen_ai_suggestion_total` | Counter | Total AI suggestions offered |

### Prometheus Recording Rules (ai:* namespace)

These are computed by Prometheus from the raw metrics above.

| Recording Rule | Type | Expression | Description |
|---|---|---|---|
| `ai:llm_request_latency_p99:seconds` | Gauge | `histogram_quantile(0.99, sum(rate(gen_ai_client_operation_duration_bucket[5m])) by (le)) or vector(0)` | P99 LLM response time |
| `ai:llm_request_latency_p50:seconds` | Gauge | `histogram_quantile(0.50, sum(rate(gen_ai_client_operation_duration_bucket[5m])) by (le)) or vector(0)` | P50 (median) LLM response time |
| `ai:token_usage_rate:per_minute` | Gauge | `sum(rate(gen_ai_client_token_usage_sum[5m])) or vector(0)` | Token consumption rate |
| `ai:suggestion_acceptance_rate:ratio` | Gauge | `0` (placeholder) | Fraction of suggestions accepted by developers (placeholder until AI SDK emits acceptance metrics) |

All recording rules are guarded with `or vector(0)` to prevent gaps during cold start.

---

## Alert Reference

All AI alerts carry `category: ai-capability` label for routing and dashboard filtering.

| Alert | Severity | Threshold | For | DORA 2025 Band |
|---|---|---|---|---|
| `AILLMLatencyHigh` | warning | P99 > 10s | 5m | Low (needs improvement) |
| `AILLMLatencyHighAbsent` | warning | metric absent | 5m | — |
| `AIReworkRateHigh` | warning | rework > 10% | 7d | Medium (watch threshold) |
| `AIReworkRateHighAbsent` | warning | metric absent | 5m | — |
| `AIReworkRateCritical` | critical | rework > 20% | 7d | Low (stop-features threshold) |
| `AIReworkRateCriticalAbsent` | critical | metric absent | 5m | — |
| `AITokenBudgetHigh` | warning | tokens > 100K/min | 5m | — |
| `AITokenBudgetHighAbsent` | warning | metric absent | 5m | — |

The 7-day `for` duration on rework rate alerts reflects DORA's trend-based approach:
a single bad day is noise; a sustained pattern requires action.

**Runbook:** See `docs/ai-runbook.md` for triage steps for each alert.

---

## Grafana Dashboard

The **AI Capabilities** dashboard is provisioned at `dashboards/platform/ai-capabilities.json`
and auto-loaded by Grafana under the **Platform** folder.

### Dashboard URL

```
http://localhost:3000/d/platform-ai-capabilities/platform-ai-capabilities
```

### Panel Guide

| Row | Panel | Type | What to Look For |
|---|---|---|---|
| 1 | P99 LLM Latency | stat (background) | Green (< 1s Elite), Yellow (1-5s High), Orange (5-10s Medium), Red (> 10s Low) |
| 1 | Token Usage Rate | stat | Count per minute; yellow > 50K, red > 100K |
| 1 | Suggestion Acceptance Rate | stat | Green (> 90% Elite), Yellow (> 75% High), Orange (> 50% Medium), Red (< 50% Low) |
| 1 | AI Rework Rate | stat | Green (< 5% Elite), Yellow (5-10% High), Orange (10-20% Medium), Red (> 20% Low) |
| 2 | LLM Latency P99/P50 | timeseries | Two lines; P99 should stay below 1s for Elite performance |
| 2 | Token Usage Rate | timeseries | Trend over time; watch for sudden spikes |
| 3 | Suggestion Acceptance Rate | timeseries | Long-term trend — declining acceptance signals instruction quality issues |
| 3 | AI Rework Rate | timeseries | This is the DORA north star: rising rework means fix AI instructions |
| 4 | AI Active Alerts | alert list | Shows all firing `category=ai-capability` alerts |

### Interpreting the Dashboard

**When data is absent:** If no AI SDK is emitting telemetry, all panels show `0` or `N/A`.
The `AILLMLatencyHighAbsent` and `AITokenBudgetHighAbsent` alerts fire to indicate the
metrics are not flowing.

**Rework rate proxy:** The rework rate is currently derived from acceptance rate
(`1 - acceptance rate`). This is a proxy until DORA recording rules provide a direct
rework metric. When `ai:suggestion_acceptance_rate:ratio` returns 0 (placeholder),
rework rate shows 100% — ignore this until AI SDK emits real acceptance data.

---

## Instrumenting Your Application

### Python

```python
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

exporter = OTLPMetricExporter(endpoint="http://otel-collector:4317")
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("my-ai-service", "0.1.0")

# Record LLM request duration
histogram = meter.create_histogram(
    name="gen_ai.client.operation.duration",
    description="Gen AI operation duration",
    unit="s",
    boundaries=[0.1, 0.5, 1, 2.5, 5, 10, 30, 60],
)
histogram.record(1.2, {"gen_ai.system": "openai", "gen_ai.request.model": "gpt-4"})

# Record token usage
counter = meter.create_counter(
    name="gen_ai.client.token.usage",
    description="Gen AI token usage",
    unit="1",
)
counter.add(150, {"gen_ai.system": "openai", "gen_ai.request.model": "gpt-4"})
```

### Environment Variables

Set these in your application's runtime environment to send telemetry to uFawkesObs:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=my-ai-service
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=none        # Only metrics needed for AI observability
OTEL_TRACES_EXPORTER=none      # Only metrics needed for AI observability
```

### Required Attributes

The following OTel semantic convention attributes are recommended for AI metrics:

| Attribute | Type | Example | Description |
|---|---|---|---|
| `gen_ai.system` | string | `openai`, `anthropic`, `google` | AI provider |
| `gen_ai.request.model` | string | `gpt-4`, `claude-3-opus` | Model name |
| `gen_ai.response.finish_reason` | string | `stop`, `length`, `error` | Response status |

---

## DORA 2025 Performance Bands

The dashboard applies these thresholds to classify AI capability metrics:

### LLM Latency (P99)

| Band | Threshold | Color | Action |
|---|---|---|---|
| **Elite** | < 1s | Green | Monitor |
| **High** | 1–5s | Yellow | Monitor |
| **Medium** | 5–10s | Orange | Investigate |
| **Low** | >= 10s | Red | Alert fires (`AILLMLatencyHigh`) |

### Suggestion Acceptance Rate

| Band | Threshold | Color | Action |
|---|---|---|---|
| **Elite** | > 90% | Green | Monitor |
| **High** | 75–90% | Yellow | Monitor |
| **Medium** | 50–75% | Orange | Investigate |
| **Low** | <= 50% | Red | Review AI instructions |

### AI Rework Rate

| Band | Threshold | Color | Action |
|---|---|---|---|
| **Elite** | < 5% | Green | Monitor |
| **High** | 5–10% | Yellow | Watch threshold — `AIReworkRateHigh` fires at > 10% |
| **Medium** | 10–20% | Orange | Investigate, prepare to stop features |
| **Low** | >= 20% | Red | **Stop features** — `AIReworkRateCritical` fires |

---

## Prerequisites

Before AI observability works end-to-end:

1. **OTel Collector** — Must be running with `metrics/ai` pipeline (OBS-AI-01)
2. **Prometheus** — Must load `ai-rules.yml` recording/alert rules (OBS-AI-02)
3. **Grafana** — Must have AI Capabilities dashboard provisioned (OBS-AI-03)
4. **Application** — Must emit `gen_ai.*` metrics via OTel SDK

All four components are included in the `core` profile — just `docker compose --profile core up -d`.

---

## See Also

- `config/otel/collector.yaml` — OTel Collector config with `metrics/ai` pipeline
- `config/prometheus/rules/ai-rules.yml` — Prometheus AI recording and alert rules
- `dashboards/platform/ai-capabilities.json` — Grafana AI Capabilities dashboard
- `docs/ai-runbook.md` — Runbook for responding to AI alerts
- `docs/ADR-001-loki-version.md` / `docs/adr/ADR-004-grafana-12x-migration.md` — ADRs
- `AGENTS.md` §10 — Model selection policy for AI-related tasks
