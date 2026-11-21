---
name: observability-correlation
description: "How traces, logs and metrics link to each other in uFawkesObs Grafana provisioning, and which links are not wired yet. Use when adding a correlation, or when a click-through from one signal to another does nothing."
license: MIT
compatibility: opencode
---

# Skill: observability-correlation

What is wired in `config/grafana/provisioning/datasources/`, `config/tempo/tempo.yaml`
and Prometheus. Verified against those files; re-check before relying on it.
Ports: `obs-stack`. Query syntax: `promql`.

| Link | State | Where |
|---|---|---|
| Log -> trace | **Wired.** Loki derived field `TraceID`, regex `traceID=(\w+)`, to the `tempo` datasource. Only fires when the log line contains literal `traceID=<id>`. | Loki datasource |
| Trace -> metrics | **Wired.** `tracesToMetrics` to `prometheus`. | Tempo datasource |
| Service graph | **Wired.** Tempo `metrics_generator` runs `service-graphs` and `span-metrics`, remote-writes to Prometheus; datasource has `serviceMap` -> `prometheus` and `nodeGraph`. | `tempo.yaml`, Tempo datasource |
| Trace -> logs | **Not wired.** No `tracesToLogs` on the Tempo datasource. | add to Tempo datasource |
| Metric -> trace (exemplars) | **Not working.** Tempo sends exemplars (`send_exemplars: true`) but Prometheus has no `--enable-feature=exemplar-storage` and the Prometheus datasource has no `exemplarTraceIdDestinations`, so they are discarded. | `compose.yaml`, Prometheus datasource |
| Log-volume spike -> alert | **Not wired.** The only Loki-side alert is `UFawkesObsLokiIngestionDropped` (ingest discards), not log volume. | `config/prometheus/rules/` |

## Rules

- Datasource UIDs are `prometheus`, `tempo`, `loki`, `alertmanager`; reference
  those, never names.
- Provisioned datasources are `editable: false`; change the YAML, not the UI.
- A correlation is done when a click-through works on a running stack, not
  when the YAML validates.
