# Spec: the five DORA metrics are measurable from real pipelines

**Traces to:** [`intent.md`](intent.md) | **Plan:** [`plan.md`](plan.md)
**Status:** Draft | **Revision:** 1

## Requirements

| ID | Requirement | Tracked in |
|---|---|---|
| DC-01 | `dora/events/*.schema.json` is the contract. `docs/CONTRACTS.md` §1 lists every property and every required field of each schema, and a test fails when it doesn't | #714 |
| DC-02 | `docs/CONTRACTS.md` describes auth as implemented: `Authorization: Bearer $DORA_API_KEY` on `/event` and `/event/batch` when the key is set, and `GET /metrics` and `GET /health` open | #714 |
| DC-03 | The GitHub collectors send the bearer token when the secret is set, send `first_commit_at` and `pr_merged_at`, set `deployed_at` to when the deploy finished, and fail on a 4xx | #715 |
| DC-04 | Compute selects and orders deployment and rework events by the event's own time (`deployed_at`, `triggered_at`), not by ingest time | #716 |
| DC-05 | Compute counts `environment: production` unless `DORA_COMPUTE_ENVIRONMENTS` lists others | #716 |
| DC-06 | Each alert's summary states the unit its expression compares, and the threshold table on the overview dashboard matches the rules | #718 |
| DC-07 | No dashboard panel names a datasource that isn't provisioned | #718 |

## Design

No new service. The changes are in `dora/collectors/github/`,
`dora/compute/metrics_db_sqlite.py`, `docs/CONTRACTS.md`, one rules file and
two dashboards.

**Open decisions** (#717). Each is the owner's, and each changes what a
consumer must do:

| # | Question | Why it matters |
|---|---|---|
| D1 | Does the deployment event accept `deployment_intent` (`planned`, `unplanned_rework`)? | uFawkesAI's emitter sends it as required. The schema has `additionalProperties: false`, so today the event is rejected with 422 |
| D2 | Do `dora_cfr_pct` and `dora_rework_rate_pct` keep their names? | Both hold a 0 to 1 ratio. A rename breaks the Dojo's Module 14 lab and fawkes's copied dashboards |
| D3 | Do `pr` and `incident` events feed a metric, or leave the contract? | Both are accepted and stored, and compute reads neither. Recovery time is the gap between a failed deployment and the next success, not an incident's duration |

## Interfaces

This changes uFawkesObs's "DORA event ingestion" row in the suite's
[cross-repo interface contracts](https://github.com/paruff/uFawkes.dev/blob/main/docs/ai-sdlc/suite-release/spec.md#cross-repo-interface-contracts).
Under the [v1.0.0 semver rules](../v1.0.0/spec.md#semver-rules):

- DC-01 to DC-03 change documents and collectors, not the wire format: patch.
- DC-04 and DC-05 change what the metrics count without renaming them: minor,
  with an upgrade note.
- D1 as "accept" adds an optional field: minor. D2 as "rename" is major.

The suite checks every copy of the schemas with AC-SUITE-04
(paruff/uFawkes.dev#232).

## Concerns

| Risk | Handling |
|---|---|
| DC-04 moves existing events into different windows, so a team's numbers change on upgrade | An upgrade note states it, and the release notes show before and after on the sample data |
| DC-05 drops staging deployments that a team was counting | `DORA_COMPUTE_ENVIRONMENTS` restores them; the default is stated in `.env.example` |
| A collector that fails on a 4xx (DC-03) turns a contract mistake into a red pipeline | That is the point: a 422 logged as a warning is how lead time went missing. The step can be made non-blocking by its caller |

## Acceptance Criteria

- **AC-01:** DC-01 and DC-02 hold. The contract test passes, and fails when a
  property is removed from the §1 table.
- **AC-02:** DC-03 holds. A run of `example-consumer.yml` against a stack
  started with `DORA_API_KEY` set returns 201, and `dora_lead_time_p50_hours`
  has a sample for that repo.
- **AC-03:** DC-04 and DC-05 hold. Unit tests cover a backfilled event and a
  staging event.
- **AC-04:** D1, D2 and D3 are answered in this file, each with a follow-up
  issue for the change it calls for.
- **AC-05:** DC-06 and DC-07 hold. `make test-unit` passes.
