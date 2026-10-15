# Plan: SLO burn-rate alerts and CFR-triggered rollback

**Traces to:** #502 (depends on #182, the live rollback drill)

## Changes

1. `config/prometheus/rules/ufawkesobs-slo-burn-rate.yml`: scrape-availability
   SLO (99.5% / 30d) with multi-window burn-rate alerts, plus
   `DORACFRRegressionRollback` (`action: rollback`). Registered in `prometheus.yaml`.
2. `.github/workflows/cfr-rollback.yml`, `scripts/cfr-alert-firing.sh`,
   `scripts/rollback-latest-good.sh`: poll the alert, roll the host back to
   `deploy-latest-good`. Off unless `CFR_AUTO_ROLLBACK_ENABLED=true`.
3. `docs/runbooks/slo-burn-rate.md`, plus a guard-check fix for intentional
   `:raw` rules and an ARCHITECTURE.md Grafana version correction.

## Verification Strategy

| Criterion                              | Evidence                                                    | How                                                   |
| -------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| Burn-rate alerts exist                 | Rules load and carry the expected severities                | `prometheus_rules.feature`; `promtool check rules`    |
| CFR regression triggers rollback       | Host moves to `deploy-latest-good`, redeploys once          | `cfr_rollback.feature` runs the real scripts          |
| No rollback when the alert is quiet    | Host stays on the candidate                                 | second scenario in `cfr_rollback.feature`             |
| Rollback is idempotent                 | Second run does not redeploy                                | first scenario in `cfr_rollback.feature`              |
| Workflow is gated and wired            | `if` checks the flag; steps call the scripts                | `tests/unit/test_cfr_rollback.py`; actionlint         |
| Not covered                            | Live-host rollback; threshold tuning (0.30 / +0.10 / 15m)   | Enable only after the #182 drill passes               |
