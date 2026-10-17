# Plan: host-metrics dashboard for OTLP agents

**Traces to:** the request to monitor developer machines and the NAS in Grafana
(companion to the Mac agent in `deploy/mac-agent/`).

## Changes

1. `dashboards/platform/host-metrics.json`: a new dashboard (uid
   `ufawkesobs-host-metrics`, schemaVersion 39) charting CPU, memory, load and
   network receive from `app_metrics_system_*` series, split by `host_name`.

No existing dashboard, rule or config changes.

## Verification Strategy

| Criterion                    | Evidence                                                        | How                                                          |
| ---------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------ |
| Dashboard conventions met    | uid prefix `ufawkesobs-`, schemaVersion 39, string datasource uid | `python3 -c 'import json; ...'` check plus `.claude/rules/dashboards.md` |
| JSON is valid                | File parses                                                     | `json.load`; pre-commit hooks                                |
| Panels show data             | Series appear for a host running the Mac agent                  | After the agent runs, Grafana panels fill; NOT yet verified  |
| Metric names are right       | `count by (host_name) ({__name__=~"app_metrics_system_.*"})`    | Run in Prometheus after first agent push; fix queries if not |
