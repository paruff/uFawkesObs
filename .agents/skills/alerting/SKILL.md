---
name: alerting
description: "Prometheus alert rule patterns and Alertmanager routing config for uFawkesObs. Load when writing new alert rules, tuning thresholds, or configuring Alertmanager receivers."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesObs
---

# Skill: Alerting (Prometheus + Alertmanager)

## Alert Rule Placement

`config/prometheus-rules/[service-name].yml` — one file per service or concern.
Loaded by Prometheus via `rule_files:` in `config/prometheus.yml`.

## Severity Levels

| Severity | Use for | Repeat interval |
|---|---|---|
| `critical` | Service down, data loss risk, DORA threshold breach | 1h |
| `warning` | Degraded performance, approaching thresholds | 4h |
| `info` | Informational, trends worth watching | 12h |

## Required Annotations

Every alert must have:
- `summary`: one sentence, includes service name
- `description`: includes `{{ $value }}` so the value is visible in the alert
- `runbook_url`: for `critical` alerts only — must be a real file in `docs/runbooks/`

## PromQL Cheat Sheet

```promql
# Rate over 5 minutes (use for counters)
rate(metric_name[5m])

# Increase over 1 hour (use for counts)
increase(metric_name[1h])

# Percentile from histogram
histogram_quantile(0.95, sum(rate(metric_bucket[5m])) by (le))

# Ratio (error rate)
sum(rate(errors[5m])) / sum(rate(requests[5m]))

# Label selector
metric{job="service-name", env="$ENVIRONMENT"}

# Humanize in annotations
{{ $value | humanize }}           # 1234 → 1.234k
{{ $value | humanizePercentage }} # 0.05 → 5%
{{ $value | humanizeDuration }}   # 125 → 2m 5s
```

## Alertmanager Receiver Templates

### Slack
```yaml
- name: slack-warnings
  slack_configs:
    - api_url: "${SLACK_WEBHOOK_URL}"
      channel: "#alerts"
      title: "{{ .GroupLabels.alertname }}"
      text: "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
      send_resolved: true
```

### Webhook (generic)
```yaml
- name: webhook
  webhook_configs:
    - url: "${ALERTMANAGER_WEBHOOK_URL}"
      send_resolved: true
      http_config:
        bearer_token: "${ALERTMANAGER_WEBHOOK_TOKEN}"
```

## Validating Rules Before Commit

```bash
# Syntax check
docker compose exec prometheus \
  promtool check rules /etc/prometheus/rules/[filename].yml

# Test a query live
curl -s "http://localhost:9090/api/v1/query?query=up" | python3 -m json.tool

# See all currently firing alerts
curl -s http://localhost:9093/api/v2/alerts | python3 -m json.tool
```

## Silence an Alert (maintenance window)

```bash
# Via Alertmanager API
curl -X POST http://localhost:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": "ServiceDown", "isRegex": false}],
    "startsAt": "2026-01-01T00:00:00Z",
    "endsAt": "2026-01-01T02:00:00Z",
    "comment": "Planned maintenance",
    "createdBy": "ops"
  }'
```