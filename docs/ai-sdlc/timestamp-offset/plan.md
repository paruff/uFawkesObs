# Plan: require a UTC offset on event timestamps

**Traces to:** AF-05 in uFawkes.dev `tests/suite-integration/AUDIT_FINDINGS.md` (the 2026-11-13 suite audit)

## Changes

1. `dora/ingestion/api/validator.py`: the `date-time` check now requires a
   time and a UTC offset (RFC 3339). `2026-11-10T10:00:00` and `2026-11-10`
   get a 422; `Z` is still accepted.
2. `dora/compute/metrics_db_sqlite.py`: lead time skips a row whose timestamps
   cannot be parsed or compared, so one stored bad row cannot abort the
   compute cycle and stop `/metrics` for every team.

## Verification Strategy

| Criterion                                 | Evidence                                                                        | How                                                                     |
| ----------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Offset-less timestamps are rejected       | `test_timestamp_without_a_utc_offset_is_rejected` (4 cases) passes              | `tests/suite-integration/run.sh` in uFawkes.dev, against this checkout  |
| One bad row cannot stop other teams       | `test_one_event_with_a_naive_timestamp_does_not_stop_metrics_for_every_team`    | Same run                                                                |
| Existing validator and compute unchanged  | 52 unit tests pass (validator, metrics sqlite, worker)                          | `pytest tests/unit/test_dora_validator.py test_dora_metrics_sqlite.py test_dora_worker.py` |
| Hooks pass                                | ruff, mypy and the other pre-commit hooks                                       | `pre-commit run --all-files`                                            |
| Not covered                               | Rows already stored with a naive timestamp are skipped from lead time, not fixed | Left as is; they leave the 30-day window on their own                   |
