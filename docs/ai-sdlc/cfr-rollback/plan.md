# Plan: CFR-triggered rollback

**Traces to:** #502 (second half; burn-rate alerts ship separately). Depends on #182.

## Changes

1. `DORACFRRegressionRollback` (+ Absent companion) in `ufawkesobs-dora-regression.yml`.
2. `.github/workflows/cfr-rollback.yml`, `scripts/cfr-alert-firing.sh`,
   `scripts/rollback-latest-good.sh`: poll the alert, roll the host back to
   `deploy-latest-good`. Off unless `CFR_AUTO_ROLLBACK_ENABLED=true`.
3. `docs/runbooks/cfr-rollback.md`.

## Verification Strategy

| Criterion                           | Evidence                                          | How                                                 |
| ----------------------------------- | ------------------------------------------------- | --------------------------------------------------- |
| CFR regression triggers rollback    | Host moves to `deploy-latest-good`, redeploys once | `cfr_rollback.feature` runs the real scripts       |
| No rollback when the alert is quiet | Host stays on the candidate                       | second scenario in `cfr_rollback.feature`           |
| Rollback is idempotent              | Second run does not redeploy                      | first scenario in `cfr_rollback.feature`            |
| Alert exists with `action: rollback` | Rule loads with expected labels                  | `prometheus_rules.feature`; `promtool check rules`  |
| Workflow is gated and wired         | `if` checks the flag; steps call the scripts      | `tests/unit/test_cfr_rollback.py`; actionlint       |
| Not covered                         | Live-host rollback; thresholds (0.30 / +0.10 / 15m) | Enable only after the #182 drill passes           |
