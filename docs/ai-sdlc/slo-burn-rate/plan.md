# Plan: SLO burn-rate alerts

**Traces to:** #502 (first half; the CFR rollback ships separately)

## Changes

1. `config/prometheus/rules/ufawkesobs-slo-burn-rate.yml`: scrape-availability
   SLO (99.5% / 30d) with multi-window burn-rate alerts; registered in
   `prometheus.yaml`.
2. `docs/runbooks/slo-burn-rate.md`.
3. The recording-rule guard check now exempts intentional `:raw` rules (#533),
   and ARCHITECTURE.md's Grafana version matches compose.

## Verification Strategy

| Criterion                      | Evidence                                           | How                                                    |
| ------------------------------ | -------------------------------------------------- | ------------------------------------------------------ |
| Burn-rate alerts exist         | Rules load with the expected severities            | `prometheus_rules.feature`; `promtool check rules`     |
| Rules are loaded by Prometheus | File listed in `rule_files`                        | `test_prometheus_config_validation.py`                 |
| Guard check still catches gaps | Only `:raw` records are exempt                     | `all recording rules should be guarded` scenarios pass |
| Not covered                    | SLO target and burn thresholds are judgement calls | Tune after observing real error ratios                 |
