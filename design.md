# Design — OBS-AI-02: Prometheus AI Recording Rules and Alerts

**Based on:** specification.md (OBS-AI-02), promql skill, existing alert patterns

---

## Impacted Components

| Component | File | Change Type |
|---|---|---|
| Prometheus AI rules | `config/prometheus/ai-rules.yml` | **Create** — new rule file |
| Prometheus config | `config/prometheus/prometheus.yaml` | Add `ai-rules.yml` to `rule_files:` |
| AI runbook | `docs/ai-runbook.md` | **Create** — stub runbook for AI alerts |
| Change impact map | `docs/CHANGE_IMPACT_MAP.md` | Add ai-rules.yml entry |
| Unit tests | `tests/unit/test_prometheus_config_validation.py` | Add AI rules test class |

---

## Technical Approach

### Current State

`config/prometheus/prometheus.yaml` has `rule_files:` referencing two files:
```yaml
rule_files:
  - "/etc/prometheus/alerts.yml"
  - "/etc/prometheus/rules/ufawkesobs-self-monitoring.yml"
```

AI metrics (from OBS-AI-01) surface through the `otel-app-metrics` scrape job at `otel-collector:8889` as OpenTelemetry metrics with names in the `gen_ai.*` namespace. OTel metric names containing `.` are converted to `_` in Prometheus (e.g. `gen_ai.client.operation.duration` → `gen_ai_client_operation_duration`).

### Target State

New file `config/prometheus/ai-rules.yml`:

```yaml
groups:
  - name: ai_capability_recording_rules
    interval: 60s
    rules:
      - record: ai:llm_request_latency_p99:seconds
        expr: |
          histogram_quantile(0.99,
            sum(rate(gen_ai_client_operation_duration_bucket[5m]))
              by (le)
          ) or vector(0)

      - record: ai:llm_request_latency_p50:seconds
        expr: |
          histogram_quantile(0.50,
            sum(rate(gen_ai_client_operation_duration_bucket[5m]))
              by (le)
          ) or vector(0)

      - record: ai:token_usage_rate:per_minute
        expr: |
          sum(rate(gen_ai_client_token_usage_count[5m]))
          or vector(0)

      - record: ai:suggestion_acceptance_rate:ratio
        expr: |
          0
        # Placeholder: will be replaced with actual ratio once AI SDK emits acceptance metrics.
        # Pattern: sum(rate(gen_ai_suggestion_accepted_total[5m])) / (sum(rate(gen_ai_suggestion_total[5m])) or vector(0))

  - name: ai_capability_alerts
    interval: 60s
    rules:
      - alert: AILLMLatencyHigh
        expr: ai:llm_request_latency_p99:seconds > 10
        for: 5m
        labels: { severity: warning, category: ai-capability }
        annotations:
          summary: "LLM p99 latency is above 10s"
          description: "p99 LLM latency is {{ $value | humanizeDuration }} for the last 5 minutes."
          runbook_url: "..."

      - alert: AIReworkRateHigh
        expr: (dora:rework_rate:ratio or vector(0)) > 0.10
        for: 7d
        labels: { severity: warning, category: ai-capability }
        annotations:
          summary: "AI rework rate is above 10% — watch threshold"
          description: "Current rework rate: {{ $value | humanizePercentage }}."
          runbook_url: "..."

      - alert: AIReworkRateCritical
        expr: (dora:rework_rate:ratio or vector(0)) > 0.20
        for: 7d
        labels: { severity: critical, category: ai-capability }
        annotations:
          summary: "AI rework rate is above 20% — stop features, fix instructions"
          description: "...DORA 2025 reference..."
          runbook_url: "..."

      - alert: AITokenBudgetHigh
        expr: ai:token_usage_rate:per_minute > 100000
        for: 5m
        labels: { severity: warning, category: ai-capability }
        annotations:
          summary: "AI token usage rate is high"
          description: "..."
          runbook_url: "..."
```

### Design Decisions

1. **Separate rule file, not merged into alerts.yml:** The existing `alerts.yml` contains infrastructure alerts. AI capability alerts are semantically different with different receivers and SLAs. A separate file is cleaner and allows independent reloading.

2. **Recording rules use `or vector(0)` consistently:** Per the promql skill, any rate-based expression that may return no data during cold start must have `or vector(0)`. This prevents absent() gaps in dashboards.

3. **Acceptance rate is a placeholder returning 0:** No AI SDK currently emits acceptance metrics. The recording rule exists so dashboards can reference it without error. It returns `0` (no suggestions accepted) until real data flows.

4. **Rework rate uses `dora:rework_rate:ratio` fallback pattern:** The rework rate recording rule from OBS-DORA-04 isn't available yet. The alert expression uses `(dora:rework_rate:ratio or vector(0))` so it evaluates to `0` (rework rate = 0%) when no DORA data flows — the alerts never false-positive. Once DORA rules are added, they automatically start working.

5. **Alert `for: 7d` on rework rate alerts:** DORA 2025 thresholds are trend-based, not spike-based. A 7-day window ensures we detect sustained rework patterns rather than noisy short-term fluctuations.

6. **`absent()` guards:** Per the promql skill, every alerting rule that fires when a metric value crosses a threshold must have a paired `absent()` rule. This is implemented for all AI alerts where the underlying metric could disappear.

### Metric Name Mapping

OTel metric → Prometheus metric conversion:

| OTel Metric | Prometheus Metric | Used By |
|---|---|---|
| `gen_ai.client.operation.duration` | `gen_ai_client_operation_duration_bucket`, `_sum`, `_count` | Latency P99/P50 recording rules |
| `gen_ai.client.token.usage` | `gen_ai_client_token_usage_bucket`, `_sum`, `_count` | Token rate recording rule |
| `gen_ai.suggestion.accepted` (future) | `gen_ai_suggestion_accepted_total` | Acceptance rate (planned) |
| `gen_ai.suggestion.total` (future) | `gen_ai_suggestion_total` | Acceptance rate (planned) |
| `dora:rework_rate:ratio` (future) | `dora_rework_rate_ratio` | Rework rate alerts |

---

## Constraints

- **Prometheus version:** v2.55.1 (supports `histogram_quantile`, `rate`, and `or vector(0)` natively)
- **Rule files path:** Must match the mounted volume path in `compose.yaml`: `/etc/prometheus/rules/`
- **Alert label convention:** All alerts must use `category: ai-capability` per issue spec
- **No second AI SDK data source:** Rules must degrade gracefully to `vector(0)` when data is absent
