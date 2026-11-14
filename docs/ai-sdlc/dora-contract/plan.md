# Plan: the five DORA metrics are measurable from real pipelines

**Traces to:** [`spec.md`](spec.md) → [`intent.md`](intent.md)

This plan lists no tasks. They are the sub-issues of #719 on
[Project #7](https://github.com/users/paruff/projects/7).

## Sequence

1. **Decide D1 to D3** (#717). D1 unblocks uFawkesAI's emitter
   (paruff/uFawkesAI#287); D2 decides whether the next release is a major.
2. **Make the contract true** (#714). It changes no behaviour, so it can
   merge first and gives uFawkesPipe's mirror check (paruff/uFawkesPipe#218)
   something correct to compare with.
3. **Fix the collectors** (#715), then **the compute window and environment
   filter** (#716). Each is one PR with its upgrade note.
4. **Alerts and dashboards** (#718), last, so their text describes the
   metrics as #716 leaves them.

## Verification Strategy

| Criterion | Evidence | How |
|---|---|---|
| AC-01 | The contract test fails when a schema property is missing from `docs/CONTRACTS.md` §1 | `make test-unit` |
| AC-02 | A 201 from a stack with `DORA_API_KEY` set, and a `dora_lead_time_p50_hours` sample | A real run of `example-consumer.yml`; `make up-dora` first |
| AC-03 | A backfilled event lands in the window of its `deployed_at`; a staging event isn't counted | `make test-unit` |
| AC-04 | Three answers in `spec.md`, each with an issue | Review |
| AC-05 | Alert text and the threshold table match the rules; no panel on a missing datasource | `make test-unit`; `promtool check rules` through `make validate-configs` |
| Not covered | Whether uFawkesPipe and uFawkesAI send the fields | paruff/uFawkesPipe#223, paruff/uFawkesAI#291, and the suite's AC-SUITE-04 |
