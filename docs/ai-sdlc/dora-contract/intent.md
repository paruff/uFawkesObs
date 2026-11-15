# Intent: the five DORA metrics are measurable from real pipelines

uFawkesObs#719. Found by the suite audit of 2026-11-13, which read every
suite repo at `main` and ran nothing.

## Problem

The stack computes five DORA metrics, but only deployment frequency gets data
from a real pipeline:

- Lead time is computed from `first_commit_at` or `pr_merged_at` on the
  deployment event. uFawkesPipe's `notify-obs` and this repo's GitHub
  collector send neither.
- Every sender reports `status: success` only, so change failure rate and
  failed deployment recovery time have nothing to count.
- Rework rate needs a `rework` event. Only the backfill script sends one.

The contract that senders read is also wrong in places. `docs/CONTRACTS.md`
§1 omits two fields the schema accepts and says auth isn't enforced, which it
is when `DORA_API_KEY` is set. uFawkesPipe's mirror and uFawkesAI's test copy
of the deployment schema both differ from `dora/events/`.

## Desired outcome

A repo that wires a collector the way the docs say gets all five metrics,
computed over production deployments in the window they happened in. One
file defines each event, and every description or copy of it is checked
against that file.

## Out of scope

- uFawkesPipe's and uFawkesAI's senders (paruff/uFawkesPipe#223,
  paruff/uFawkesAI#291). This repo fixes its own collectors and its contract.
- New metrics or dashboards.
- fawkes's own Prometheus rules (paruff/fawkes#2314).
