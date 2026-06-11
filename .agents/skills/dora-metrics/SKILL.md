---
name: dora-metrics
description: "DORA metric queries for uFawkesObs: PromQL expressions for deployment frequency, lead time, change failure rate, and FDRT sourced from deployment spans processed by the OTel Collector. Load when writing DORA dashboards or interpreting DORA metric data in Prometheus."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesObs
---

# Skill: DORA Metrics (uFawkesObs)

## How DORA Metrics Reach Prometheus

Services emit OTLP span events → OTel Collector → spanmetrics processor converts spans to Prometheus counters → Prometheus scrapes → Grafana queries.

**Required spans from services:**

```
deployment.completed  { service, version, environment, duration_ms, status }
deployment.failed     { service, version, environment, error }
incident.opened       { service, severity }
incident.resolved     { service, severity, duration_ms }
```

**If these spans are not emitted:** DORA metrics will be absent from Prometheus. Verify with: `curl -s http://localhost:9090/api/v1/label/__name__/values | grep deployment`

## PromQL Queries

### Deployment Frequency (deployments per day)

```promql
increase(deployment_completed_total{environment="prod"}[1d])
```

### Change Failure Rate

```promql
sum(rate(deployment_failed_total{environment="prod"}[7d]))
/
sum(rate(deployment_completed_total{environment="prod"}[7d])) * 100
```

### Failed Deployment Recovery Time (FDRT / MTTR)

```promql
# Average recovery duration in seconds
avg(incident_duration_seconds{severity=~"critical|high"})
```

### Lead Time (proxy — PR merge to deployment)

```promql
# Requires deployment spans to carry commit_timestamp attribute
# If available:
avg(deployment_lead_time_seconds{environment="prod"})
```

**Note:** Lead time is the hardest to measure via spans alone. If `deployment_lead_time_seconds` is absent from Prometheus, lead time tracking requires integration with the GitHub API or DevLake (the approach used in full fawkes deployments).

## DORA Thresholds for Alert Rules

| Metric               | Warning         | Critical          |
| -------------------- | --------------- | ----------------- |
| Change failure rate  | > 15%           | > 30%             |
| FDRT                 | > 1 day         | > 7 days          |
| Deployment frequency | Declining trend | Zero for > 7 days |

## Grafana DORA Dashboard Variables

```json
"templating": {
  "list": [
    {
      "name": "service",
      "type": "query",
      "datasource": { "uid": "prometheus" },
      "query": "label_values(deployment_completed_total, service)"
    },
    {
      "name": "environment",
      "type": "query",
      "datasource": { "uid": "prometheus" },
      "query": "label_values(deployment_completed_total, environment)",
      "current": { "value": "prod" }
    },
    {
      "name": "range",
      "type": "interval",
      "options": ["1d", "7d", "30d", "90d"],
      "current": { "value": "30d" }
    }
  ]
}
```

## OTel Collector spanmetrics Processor Config

To convert deployment spans to Prometheus metrics, the collector needs the spanmetrics connector:

```yaml
# In config/otel-collector-config.yaml
connectors:
  spanmetrics:
    histogram:
      explicit:
        buckets: [10ms, 100ms, 500ms, 1s, 5s, 30s]
    dimensions:
      - name: service
      - name: environment
      - name: version
      - name: status
    metrics_flush_interval: 15s

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/tempo, spanmetrics]
    metrics/from-spans:
      receivers: [spanmetrics]
      exporters: [prometheusremotewrite]
```

**Verify spanmetrics is working:**

```bash
curl -s http://localhost:9090/api/v1/query?query=calls_total | python3 -m json.tool
# Should return span-derived metrics if spans are being received
```
