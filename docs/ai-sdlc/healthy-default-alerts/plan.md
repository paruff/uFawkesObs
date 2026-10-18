# Plan: a healthy default install fires no alerts

**Traces to:** #670 (items 1-3). Item 4 (Loki/Tempo `/ready` 503) is not changed.

## Changes

1. `prometheus.yaml`: scrape `dora-api` via `dns_sd_configs`, so the target
   exists only while the dora profile's container resolves.
2. `ufawkesobs-self-monitoring.yml`: `UFawkesObsContainerRestarting` needs a
   >10 s start-time shift; the Loki/OTel "dropped" alerts lose their
   `absent() * 0` fallback (it fired at value 0).
3. `ufawkesobs-dora-*.yml`: every DORA `*Absent` rule is gated on
   `up{job="dora-api"} == 1`.
4. `alerts.yml`: OTel memory/CPU rules use `otelcol_process_*`;
   `PrometheusSlowQueries` reads the summary metric; storage-full ignores a
   retention limit of 0.

## Verification Strategy

| Criterion                                   | Evidence                                              | How                                                          |
| ------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| No alert fires on a healthy default install | `GET /api/v1/alerts` returns 0 after 30 min           | fresh clone, README `make up` on Linux (Lima); posted on #670 |
| dora-api only scraped under the dora profile | No `dora-api` target by default; target `up` when run | throwaway Prometheus plus a fake `dora-api` container        |
| DORA absent guards still target raw series  | Expression is `absent(<raw>)` plus the dora-api gate  | `tests/unit/test_dora_metrics_alerts.py`                     |
| Scrape job shape                            | `dns_sd` on `dora-api:8088`, no `static_configs`      | `tests/unit/test_dora_regression_alerts.py`                  |
| Rules load                                  | `promtool check config` succeeds                      | run inside the Prometheus container                          |
| Not covered                                 | Clean macOS `make up`; a crashed dora-api no longer raises ServiceDown | tracked on #670                                 |
