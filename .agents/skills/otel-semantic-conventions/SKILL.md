---
name: otel-semantic-conventions
description: OpenTelemetry semantic convention reference for uFawkesObs, focused on gen_ai.* metric and span attribute namespace for AI observability (Wave 5).
license: MIT
compatibility: opencode
---

# Skill: otel-semantic-conventions

## Purpose

OpenTelemetry semantic convention reference for uFawkesObs, focused on the conventions needed for Wave 5 (AI observability). Covers the `gen_ai.*` metric and span attribute namespace, which is required for OBS-AI-\* issues.

Load this skill for any task involving AI/LLM telemetry instrumentation or the `gen_ai.*` metric namespace.

**Dependency:** Wave 5 requires OTel Collector 0.120+ (already at target). Verify via `component-versions` skill before implementing any gen_ai.\* pipeline work.

---

## gen_ai.\* — the AI/LLM semantic conventions

These are the OTel semantic conventions for generative AI systems. They define the standard attribute names for LLM spans and metrics.

### Span attributes (traces)

| Attribute                        | Type     | Description                                                     |
| -------------------------------- | -------- | --------------------------------------------------------------- |
| `gen_ai.system`                  | string   | LLM provider: `openai`, `anthropic`, `aws.bedrock`, `vertex_ai` |
| `gen_ai.request.model`           | string   | Model requested: `gpt-4`, `claude-3-opus`, etc.                 |
| `gen_ai.response.model`          | string   | Actual model that responded (may differ from request)           |
| `gen_ai.request.max_tokens`      | int      | Max tokens requested                                            |
| `gen_ai.usage.input_tokens`      | int      | Tokens in the prompt                                            |
| `gen_ai.usage.output_tokens`     | int      | Tokens in the completion                                        |
| `gen_ai.operation.name`          | string   | `chat`, `text_completion`, `embeddings`                         |
| `gen_ai.request.temperature`     | float    | Temperature setting                                             |
| `gen_ai.request.top_p`           | float    | Top-p setting                                                   |
| `gen_ai.response.finish_reasons` | string[] | `stop`, `length`, `content_filter`                              |
| `gen_ai.response.id`             | string   | Response ID from provider                                       |

### Metric names (metrics)

| Metric                              | Type      | Unit      | Description                                                |
| ----------------------------------- | --------- | --------- | ---------------------------------------------------------- |
| `gen_ai.client.token.usage`         | Histogram | `{token}` | Distribution of token usage per request                    |
| `gen_ai.client.operation.duration`  | Histogram | `s`       | Duration of LLM operations                                 |
| `gen_ai.server.request.duration`    | Histogram | `s`       | Server-side request duration (if instrumenting the server) |
| `gen_ai.server.time_to_first_token` | Histogram | `s`       | Latency to first token in streaming responses              |

### Standard labels on gen_ai metrics

Every gen_ai metric will carry these labels:

- `gen_ai.system` — the LLM provider
- `gen_ai.request.model` — the model name
- `gen_ai.operation.name` — the operation type

---

## PromQL queries for AI metrics (Wave 5 recording rules)

### Token consumption rate

```promql
# Total tokens per minute, by system and model
sum(rate(gen_ai_client_token_usage_total[5m])) by (gen_ai_system, gen_ai_request_model)
or vector(0)
```

Note: OTel metric names use `.` but Prometheus converts `.` to `_` in metric names. `gen_ai.client.token.usage` becomes `gen_ai_client_token_usage`.

### P95 operation latency

```promql
histogram_quantile(0.95,
  sum(rate(gen_ai_client_operation_duration_bucket[5m]))
    by (le, gen_ai_system, gen_ai_request_model)
)
```

### Error rate (if error events are instrumented)

```promql
sum(rate(gen_ai_client_operation_duration_count{error_type!=""}[5m]))
  by (gen_ai_system, gen_ai_request_model)
/
(sum(rate(gen_ai_client_operation_duration_count[5m]))
  by (gen_ai_system, gen_ai_request_model)
  or vector(0))
```

---

## OTel Collector config for gen_ai.\* pipeline (Wave 5)

Add a **separate** pipeline — do not modify the default metrics pipeline:

```yaml
processors:
  filter/ai:
    metrics:
      include:
        match_type: regexp
        metric_names:
          - "gen_ai.*"

exporters:
  prometheusremotewrite/ai:
    endpoint: http://prometheus:9090/api/v1/write
    external_labels:
      plane: ufawkesobs
      source: ai-metrics

service:
  pipelines:
    metrics/ai:
      receivers: [otlp]
      processors: [memory_limiter, batch, filter/ai]
      exporters: [prometheusremotewrite/ai]
```

---

## Resource attributes (span context)

The `uFawkesAI` plane instruments agents that call LLMs. These resource attributes should be present on spans from uFawkesAI:

| Resource attribute       | Expected value                                  |
| ------------------------ | ----------------------------------------------- |
| `service.name`           | The agent name (e.g. `build-agent`, `ux-agent`) |
| `service.version`        | The agent version or commit SHA                 |
| `deployment.environment` | `development`, `staging`, `production`          |

Use these in dashboard filters and PromQL label selectors when building the AI capabilities dashboard.

---

## Wave 5 implementation order

1. OTel 0.120 must be deployed (already at target — verify)
2. Add `metrics/ai` pipeline to `config/otel/collector.yaml`
3. Add `gen_ai.*` recording rules to `config/prometheus/rules/ufawkesobs-ai-metrics.yml`
4. Create AI capabilities dashboard in `dashboards/ufawkesobs-ai-metrics.json`
5. Update `AGENTS.md` with the AI pipeline documentation

Do not implement DORA recording rules in this wave — that requires the human gate on M4-01.

---

## References

- OTel GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Prometheus naming conventions for OTel metrics: dots become underscores
- uFawkesAI AGENTS.md: the agent architecture that produces these spans
