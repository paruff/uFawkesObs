---
name: dora-metrics
description: "DORA metric queries for uFawkesObs: PromQL expressions for the real GitHub Actions → dora-api → Prometheus pipeline. Use this when writing DORA dashboards or validating recording rules in Prometheus."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesObs
---

# Skill: DORA Metrics (uFawkesObs)

## Real pipeline in this repo

The current pipeline is not spanmetrics-based. The actual flow is:

GitHub Actions `deploy.yml` → `scripts/send-dora-deployment-event.sh` → `dora-api` `POST /event` → SQLite event store → background compute → Prometheus `/metrics` scrape → recording rules in `config/prometheus/rules/ufawkesobs-dora-metrics.yml`.

Key implementation points:

- `deploy.yml` emits deployment events with `DORA_COMMIT_SHA` and the deployment metadata.
- The API lives in `dora/ingestion/api/` and accepts REST events (`/event`, `/event/batch`).
- `dora-api` writes to SQLite and exposes computed DORA metrics on `/metrics`.
- Prometheus scrapes the `dora-api` target and then applies the recording rules in `ufawkesobs-dora-metrics.yml`.
- the legacy span-based deployment counters do not exist in this repo; they are stale documentation from an abandoned OTLP-spans plan.

## Prometheus metrics and recording rules

The authoritative series are the recording rules generated from the DORA compute path:

```promql
dora:deployment_frequency:rate30d
dora:lead_time_hours:p50_30d
dora:change_failure_rate:ratio30d
dora:fdrt_hours:p50_30d
dora:rework_rate:ratio
```

Use these for dashboards and alerting. If you need to validate the rule file locally, run:

```bash
promtool check rules config/prometheus/rules/ufawkesobs-dora-metrics.yml
```

## Example queries

### Deployment Frequency

```promql
# successful production deployments over the last 30d
dora:deployment_frequency:rate30d
```

### Lead Time for Changes

```promql
dora:lead_time_hours:p50_30d
```

### Change Failure Rate

```promql
dora:change_failure_rate:ratio30d
```

### Failed Deployment Recovery Time (FDRT)

```promql
dora:fdrt_hours:p50_30d
```

### Rework Rate

```promql
# Official DORA rework definition: work later identified as rework / reverted
dora:rework_rate:ratio
```

## Alerting notes

This repo uses repository-specific alert thresholds and absent()-based guards, not the retired Elite/High/Medium/Low tier bands. The relevant check is currently the `dora:` recording rules file itself.

Examples:

```promql
(dora:rework_rate:ratio or vector(0)) > 0.10
(dora:rework_rate:ratio or vector(0)) > 0.20
```

## Validation checklist

Before writing rules or dashboards against a new metric, confirm all of the following:

1. The series exists in `config/prometheus/rules/ufawkesobs-dora-metrics.yml`.
2. Prometheus scrapes `dora-api:8088/metrics`.
3. `dora-api` is receiving deployment events via `.github/workflows/deploy.yml` and `scripts/send-dora-deployment-event.sh`.
4. `promtool check rules ...` succeeds for the rule file you touched.

## Do not use

Do not rely on these stale names or assumptions:

- `spanmetrics` processing of deployment spans
- legacy deployment counters that do not exist in this repo
- the retired Elite/High/Medium/Low band wording unless a directly cited report is being used
