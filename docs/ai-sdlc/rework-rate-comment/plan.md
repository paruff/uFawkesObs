# Plan: correct the rework-rate comments in the DORA rules file

**Traces to:** the DORA metric review of 2026-10-03 (uFawkes.dev#110, #115)

## Changes

1. `config/prometheus/rules/ufawkesobs-dora-metrics.yml`: two comments said
   rework rate is the "share of completed work later reverted after merge".
   The code does not compute that. `dora/compute/metrics_db_sqlite.py` divides
   user-visible rework events (hotfix, rollback or patch, matched to a
   deployment by commit SHA) by total deployments. Both comments now say so,
   and note that dora.dev words the metric more broadly (unplanned deployments
   caused by a production incident).

No rule, expression, label, alert or threshold changes.

## Verification Strategy

| Criterion                     | Evidence                                                          | How                                                              |
| ----------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------- |
| Only comments changed         | The parsed YAML before and after the edit is identical            | `yaml.safe_load` on both versions, compared with `==`            |
| The new text matches the code | It restates `rework_rate()` in `metrics_db_sqlite.py`             | Read the function; no behaviour test needed for a comment change |
| Hooks pass                    | yamllint, check-yaml, gitleaks and the other pre-commit hooks     | `pre-commit run --files <changed files>`                         |
| Not covered                   | Whether the user-visible filter is intended is a product decision | Left to the owner; the alert text still says "AI rework rate"    |
