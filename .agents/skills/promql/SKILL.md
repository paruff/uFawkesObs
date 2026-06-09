---
name: promql
description: PromQL correctness rules for uFawkesObs. Covers the specific failure modes that agents without this skill consistently produce: missing absent() guards, rate() on gauges, missing or vector(0), and irate() in recording rules.
license: MIT
compatibility: opencode
---

# Skill: promql

## Purpose

PromQL correctness rules for uFawkesObs. Covers the specific failure modes that agents without this skill consistently produce: missing absent() guards, rate() on gauges, missing or vector(0), and irate() in recording rules.

Load this skill before writing any Prometheus rule file or ad-hoc query.

---

## Metric type identification

Before writing any query, identify the metric type. Getting this wrong silently produces wrong data.

| Suffix pattern | Type | Correct function |
|---------------|------|-----------------|
| `_total` | Counter | `rate()`, `increase()` |
| `_created` | Counter (timestamp) | Usually skip |
| `_bytes_total`, `_requests_total` | Counter | `rate()`, `increase()` |
| `_seconds` (no `_total`) | Gauge or histogram | `avg_over_time()`, direct reference |
| `_ratio`, `_fraction` | Gauge | Direct reference or `avg_over_time()` |
| `_bucket`, `_sum`, `_count` | Histogram | `histogram_quantile()` with `rate()` on _bucket |
| `up` | Gauge (0 or 1) | Direct, `avg_over_time()` |

**Critical:** `rate()` on a gauge returns meaningless results. It will not error — it will silently return wrong data.

---

## Recording rules

### Required structure

```yaml
groups:
  - name: ufawkesobs.rules
    interval: 60s        # Must match Prometheus scrape interval or longer
    rules:
      - record: job:request_rate5m:sum
        expr: sum(rate(http_requests_total[5m])) or vector(0)
```

### or vector(0) — required pattern

Any recording rule with arithmetic that may produce no series:

```yaml
# CORRECT
expr: |
  sum(rate(http_requests_total[5m]))
  or vector(0)

# CORRECT — ratio with zero protection
expr: |
  sum(rate(http_requests_errors_total[5m]))
  /
  (sum(rate(http_requests_total[5m])) or vector(0))
```

**When to apply:** Any `rate()`, `increase()`, `sum()`, or division that may return no data during cold start, gaps in scraping, or missing targets.

**When not needed:** Simple gauge references like `up` or `container_memory_usage_bytes`.

### irate() — never in recording rules

`irate()` uses only the last 2 data points. It is appropriate for real-time dashboards. In recording rules it produces meaningless pre-aggregated data.

```yaml
# WRONG in recording rules
expr: irate(http_requests_total[5m])

# CORRECT in recording rules
expr: rate(http_requests_total[5m])
```

### Naming convention (Prometheus community standard)

```
<aggregation>:<metric_name>:<additional_labels>
```

Examples:
- `job:http_request_rate5m:sum` — sum of request rate over 5m, per job
- `job_service:deployments_total:rate5m` — deployment rate per job+service

---

## Alerting rules

### Required: absent() guard for every metric-based alert

Every alerting rule that fires when a metric value crosses a threshold MUST have a paired `absent()` rule. Without it, if the target disappears, the alert silently stops firing.

```yaml
groups:
  - name: target-health
    rules:
      # Primary alert — fires when metric exists and is wrong
      - alert: PrometheusTargetDown
        expr: up{job="prometheus"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Prometheus target {{ $labels.instance }} is down"

      # Required absent() guard — fires when metric doesn't exist at all
      - alert: PrometheusTargetMissing
        expr: absent(up{job="prometheus"})
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Prometheus target up metric is missing entirely"
```

### for: duration guidance

| Scenario | Minimum `for:` |
|---------|---------------|
| Noisy metrics (request rates, error rates) | 5m |
| Infrastructure health (up, memory, disk) | 2m |
| Capacity alerts (disk filling) | 10m |
| Critical path (data loss risk) | 1m |

Never use `for: 0s` on rate-based metrics — it will flap.

### Label and annotation standards

```yaml
labels:
  severity: critical | warning | info   # Always one of these three
  plane: ufawkesobs                      # Identifies the IDP plane

annotations:
  summary: "One-line human-readable description"
  description: "Longer description with {{ $labels.instance }} and {{ $value }}"
  runbook_url: "https://github.com/paruff/uFawkesObs/blob/main/docs/runbooks/<name>.md"
```

---

## uFawkesObs self-monitoring rules (config/prometheus/rules/ufawkesobs-self-monitoring.yml)

These are the rules required for M1-03. Every rule in this file must have an `absent()` guard.

Essential alert coverage:
- OTel Collector down / absent
- Prometheus down / absent (Prometheus can't alert on itself being down — use Alertmanager deadman)
- Grafana down / absent
- Loki down / absent
- Tempo down / absent
- Alloy down / absent
- Prometheus target scrape errors > threshold
- Prometheus TSDB compaction errors

---

## DORA recording rules (Wave 6 — human gate required)

Do not implement until M4-01 has `spec-approved` label. When authorised, the key recording rules are:

```
# Deployment frequency (requires deployment event labels from uFawkesPipe)
job_service:deployments_total:rate1h
job_service:deployments_total:rate24h

# Change failure rate (requires failed_deployment label)
# Lead time for change (requires commit_timestamp label — cross-plane dependency)
```

These are placeholders only. Implementation requires the DORA data contract spec.

---

## Validation command

```bash
promtool check rules config/prometheus/rules/<file>.yml
```

Must pass before any PR. Also validate the full config:
```bash
promtool check config config/prometheus/prometheus.yaml
```
