# Design — OBS-AI-03: Grafana AI Capabilities Dashboard

**Based on:** specification.md (OBS-AI-03), dashboard-authoring skill, grafana-provisioning skill

---

## Impacted Components

| Component | File | Change Type |
|---|---|---|
| AI dashboard | `dashboards/platform/ai-capabilities.json` | **Create** — new dashboard JSON |

---

## Technical Approach

### Current State

`dashboards/platform/` contains 9 platform dashboards loaded by `new-dashboards.yaml` provider
via volume mount `./dashboards/platform:/etc/grafana/dashboards/platform:ro`. No AI-specific
dashboard exists.

AI metrics surface through Prometheus from two sources:
1. **OTel `metrics/ai` pipeline** (OBS-AI-01): OTel Collector at `:8889` exports `gen_ai.*` metrics
2. **Recording rules** (OBS-AI-02): Pre-computed metrics like `ai:llm_request_latency_p99:seconds`

### Target State

New file `dashboards/platform/ai-capabilities.json` with 4 stat panels, 4 time-series panels,
and 1 alert list panel.

### Dashboard Layout

```
Row 1: AI Performance Summary
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ P99 Lat  │ │Token Rate│ │Acceptance│ │Rework    │
│  (stat)  │ │  (stat)  │ │Rate(stat)│ │Rate(stat)│
│ thresholds│ │          │ │thresholds│ │DORA bands│
└──────────┘ └──────────┘ └──────────┘ └──────────┘

Row 2: LLM Performance
┌──────────────────────────┐ ┌──────────────────────────┐
│ LLM Latency P99/P50      │ │ Token Usage Rate         │
│     (timeseries)         │ │     (timeseries)         │
└──────────────────────────┘ └──────────────────────────┘

Row 3: AI Quality
┌──────────────────────────┐ ┌──────────────────────────┐
│ Suggestion Acceptance    │ │ AI Rework Rate           │
│     (timeseries)         │ │     (timeseries)         │
└──────────────────────────┘ └──────────────────────────┘

Row 4: Alerts
┌──────────────────────────────────────────────────────┐
│ AI Active Alerts (alert list)                        │
└──────────────────────────────────────────────────────┘
```

### Panel Queries

| Panel | PromQL Expression | Type |
|---|---|---|
| P99 Latency | `ai:llm_request_latency_p99:seconds` | stat |
| Token Rate | `ai:token_usage_rate:per_minute` | stat |
| Acceptance Rate | `ai:suggestion_acceptance_rate:ratio * 100` | stat |
| Rework Rate | `(1 - (ai:suggestion_acceptance_rate:ratio or vector(0))) * 100` | stat |
| Latency P99/P50 | `ai:llm_request_latency_p99:seconds` / `ai:llm_request_latency_p50:seconds` | timeseries |
| Token Rate | `ai:token_usage_rate:per_minute` | timeseries |
| Acceptance Trend | `ai:suggestion_acceptance_rate:ratio * 100` | timeseries |
| Rework Trend | `(1 - (ai:suggestion_acceptance_rate:ratio or vector(0))) * 100` | timeseries |
| AI Alerts | (alert list datasource) | alertlist |

### DORA 2025 Performance Bands

**Latency thresholds (P99):**
- Elite: < 1s (green)
- High: < 5s (yellow)
- Medium: < 10s (orange)
- Low: >= 10s (red)

**Rework rate thresholds:**
- Elite: < 5% (green)
- High: < 10% (yellow)
- Medium: < 20% (orange)
- Low: >= 20% (red — "stop features" threshold)

**Acceptance rate thresholds:**
- Elite: > 90% (green)
- High: > 75% (yellow)
- Medium: > 50% (orange)
- Low: <= 50% (red)

---

## Constraints

1. **Grafana version:** 12.3.7 — use `schemaVersion: 40`
2. **Datasource UIDs:** Must use `prometheus` (string), never numeric IDs
3. **Dashboard path:** Must be `dashboards/platform/ai-capabilities.json` for auto-provisioning
4. **Metric availability:** AI metrics only exist when an AI SDK emits `gen_ai.*` data.
   Dashboard must degrade gracefully to `0` or `N/A` when data is absent.
5. **No changes to compose.yaml, provisioning YAML, or Prometheus config**
