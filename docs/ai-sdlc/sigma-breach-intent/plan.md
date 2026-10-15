# Plan: σ-band breach opens an intent issue

**Traces to:** [`intent.md`](intent.md) | uFawkesObs#602

## Changes

1. `config/prometheus/rules/ufawkesobs-sigma-band.yml`: `dora:badness_zscore_30d`
   recording rule and the `DORASigmaBandBreach` alert (>3σ for 24h); registered
   in `prometheus.yaml`.
2. `scripts/sigma-breach-intent.sh`: reads firing alerts, opens one
   deduplicated `intent` issue per team and metric in the repo named by `team_id`.
3. `.github/workflows/sigma-breach-intent.yml`: hourly poll, off unless
   `SIGMA_INTENT_ENABLED=true`; needs secret `SUITE_ISSUES_TOKEN`.
4. Runbook section in `docs/runbooks/dora.md`.

## Verification Strategy

| Criterion                            | Evidence                                             | How                                                  |
| ------------------------------------ | ---------------------------------------------------- | ---------------------------------------------------- |
| The rule is valid PromQL             | `SUCCESS: 2 rules found`                             | `promtool check rules` on the rule file              |
| A breach maps to an intent title     | Title and repo as expected, bare names get the owner | `tests/unit/test_sigma_breach_intent.py`             |
| Unsafe `team_id` never reaches `gh`  | Series skipped with a warning                        | `test_unsafe_team_id_is_skipped`                     |
| Unreadable alert state is not "none" | Non-zero exit when Prometheus is unreachable         | `test_unreachable_prometheus_fails`                  |
| Live path opens an issue             | An `intent` issue appears in a test repo             | `workflow_dispatch` after the owner sets the secrets |

## Follow-up

Enable `SIGMA_INTENT_ENABLED` and `SUITE_ISSUES_TOKEN`, and confirm the
`intent` label exists in each target repo.
