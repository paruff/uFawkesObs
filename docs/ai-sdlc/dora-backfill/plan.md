# Plan: runner-free DORA backfill from GitHub PR history

**Traces to:** "DORA shows no data" — every `dora_*` gauge comes from dora-api, which
has no events, and the GitHub runner that would post them is offline.

## Changes

1. `scripts/backfill_dora_from_github.py`: reads merged PRs with `gh`, emits
   `pr` + `deployment` events (merge to main = delivery); a PR titled "Revert …"
   becomes a `rollback` deployment plus a user-visible `rework` event. Dry-run by
   default; `--post URL` sends to `/event/batch`.
2. `tests/unit/test_backfill_dora.py`: events validate against `dora/events/*.schema.json`.
3. `docs/runbooks/dora-bringup.md`: step-by-step CLI to start the `dora` profile and backfill.

dora-api is unchanged. Known limit: it windows on ingest time, not `deployed_at`,
so only the last `--days` (default 30) are sent and FDRT gaps collapse for a backfill.

## Verification Strategy

| Criterion                      | Evidence                                              | How                                                       |
| ------------------------------ | ----------------------------------------------------- | --------------------------------------------------------- |
| Events match the contract      | Each generated event passes its JSON Schema           | `pytest tests/unit/test_backfill_dora.py`                 |
| Revert handling                | rollback deployment + matching rework event           | same test file                                            |
| Reads real history             | 188 PRs → 376 events for uFawkesObs, 30 days (dry-run) | `scripts/backfill_dora_from_github.py paruff/uFawkesObs`  |
| Metrics appear in Grafana      | `dora_deployment_frequency_per_week` has a series     | After the runbook is executed on the NAS; NOT yet verified |
