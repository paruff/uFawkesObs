# Plan: make current-state DORA docs describe the running stack

**Traces to:** uFawkesObs#534 (§3–4)

## Changes

1. `docs/` (ARCHITECTURE, CONTRACTS, design/spec banners, fawkes-migration,
   runbooks): retire the DORA service topology the stack no longer runs
   (`dora-compute`, pushgateway, `otel-collector-dora`). The live profile is
   `dora-api` only, with in-process compute and Prometheus pull on `:8088`
   (`job_name: dora-api`).
2. `config/prometheus/rules/ufawkesobs-dora-regression.yml` — the five
   absent-annotation queries now probe `up{job="dora-api"}` — and
   `ufawkesobs-dora-metrics.yml`, whose header and annotation comments were
   repointed from the pushgateway pipeline to dora-api's in-process compute.
   Issue #266 removal notes stay as written history behind a
   one-per-(file,name) allowlist in the guard test.
3. `tests/unit/test_docs_dora_freshness.py`: new guard that fails when a
   retired service name reappears in a current-state doc. Historical files
   are allowlisted with written reasons; every exclusion is printed, never
   silent.

Out of scope: #534 §1/§2 (dashboards) and §5 (`collector-dora.yaml`) stay
open — this PR must not close #534.

## Verification Strategy

| Criterion                          | Evidence                                                        | How                                                            |
| ---------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------- |
| The guard catches the old wording  | 11 findings against the pre-fix docs (exit 1; recounted 2026-10-06 against `4b5b6ac`) | `python3 tests/unit/test_docs_dora_freshness.py` before fixes  |
| The guard passes after the fixes   | Exit 0, no findings printed                                      | Same command after the three commits                           |
| Rule files stay valid              | promtool loads all 5 rule files (18 + 6 + 12 + 22 + 10 rules at this baseline) | `make validate-configs`                              |
| The Compose comment matches reality | `docker compose config` parses; the `dora` profile lists only `dora-api` | `docker compose -f compose.yaml config`              |
| Rule expressions unchanged         | Only comment/annotation text differs; YAML parse compared        | `yaml.safe_load` before/after, compared with `==`              |
| CI agrees                          | Unit Tests / Validate Configs green on this PR                   | The PR's required checks                                       |
