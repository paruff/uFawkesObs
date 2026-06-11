---
name: dashboard-authoring
description: "Grafana dashboard JSON patterns, PromQL/LogQL/TraceQL query templates, panel types, and provisioning conventions for uFawkesObs dashboards/. Load when creating or modifying Grafana dashboards."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesObs
---

# Skill: Dashboard Authoring (Grafana / uFawkesObs)

## Provisioning Convention

Dashboards in `dashboards/` are auto-loaded by Grafana on startup via:
`config/grafana/provisioning/dashboards/default.yaml`

File naming: `[service-name]-[signal-type].json`
Examples: `obstackd-health.json`, `fawkes-dora.json`, `telemetry-generator.json`

Export a dashboard from Grafana UI: Dashboard → Share → Export → Save to file → save to `dashboards/`.

## Datasource UIDs (always use these)

| Backend    | UID          |
| ---------- | ------------ |
| Prometheus | `prometheus` |
| Loki       | `loki`       |
| Tempo      | `tempo`      |

## Dashboard JSON Skeleton

```json
{
  "title": "[Service] Overview",
  "uid": "[service-name]-overview",
  "tags": ["[service]", "[team]"],
  "refresh": "30s",
  "time": { "from": "now-1h", "to": "now" },
  "templating": { "list": [] },
  "panels": [],
  "schemaVersion": 39
}
```

## Panel Type Reference

| Panel        | Use for                                     |
| ------------ | ------------------------------------------- |
| `timeseries` | Rate, latency, resource usage over time     |
| `stat`       | Single current value (error rate %, uptime) |
| `gauge`      | Single value with thresholds                |
| `table`      | Multi-column data, top-N lists              |
| `logs`       | Loki log streams                            |
| `traces`     | Tempo trace search                          |
| `alertlist`  | Firing Prometheus alerts                    |
| `text`       | Markdown annotations, links                 |

## PromQL Query Patterns

```promql
# Counter rate
sum(rate(metric_total{job="$service"}[$__rate_interval])) by (label)

# Histogram quantile
histogram_quantile(0.95, sum(rate(metric_bucket{job="$service"}[$__rate_interval])) by (le))

# Ratio as percentage
sum(rate(errors_total[5m])) / sum(rate(requests_total[5m])) * 100

# Use $__rate_interval instead of hardcoded [5m] — Grafana sets it automatically
```

## LogQL Query Patterns

```logql
# All logs for service
{service="$service"}

# Filter by level
{service="$service"} | json | level="error"

# Count errors per minute
sum(rate({service="$service"} |= "error" [1m]))

# Extract field
{service="$service"} | json | line_format "{{.message}}"
```

## TraceQL Query Patterns

```traceql
# All spans for service
{ .service.name = "$service" }

# Slow spans
{ .service.name = "$service" && duration > 500ms }

# Error spans
{ .service.name = "$service" && status = error }

# Deployment spans
{ name = "deployment.completed" && .service = "$service" }
```

## Trace-to-Log Correlation

Add to Tempo datasource in provisioning config to enable jumping from a trace to correlated Loki logs:

```yaml
jsonData:
  tracesToLogsV2:
    datasourceUid: loki
    filterByTraceID: true
    customQuery: true
    query: '{service="${__span.tags["service.name"]}"} |= "${__span.traceId}"'
```

## Dashboard Validation

Before committing a dashboard JSON file:

```bash
# Validate JSON syntax
python3 -m json.tool dashboards/[name].json > /dev/null && echo "Valid JSON"

# Check for hardcoded datasource names (should be UIDs)
grep -i '"type": "datasource"' dashboards/[name].json

# Reload dashboards without restarting Grafana
curl -s -X POST http://admin:${GRAFANA_ADMIN_PASSWORD}@localhost:3000/api/admin/provisioning/dashboards/reload
```

## Common Mistakes

| Mistake                                        | Fix                                       |
| ---------------------------------------------- | ----------------------------------------- |
| Dashboard saved in UI but not in `dashboards/` | Export JSON → commit to repo              |
| Hardcoded datasource name instead of UID       | Replace with `{"uid": "prometheus"}` etc. |
| `[5m]` hardcoded in query                      | Replace with `[$__rate_interval]`         |
| No `$service` variable                         | Add to templating section                 |
| High-cardinality label in `by()` clause        | Remove or aggregate more broadly          |
