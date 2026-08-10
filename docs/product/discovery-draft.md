---
date: 2026-07-27
persona: solo-entrepreneur
jtbd: "When I run a small (3-15 person) engineering team shipping on Docker Compose, I want a self-hosted stack that gives me production-grade metrics, logs, traces, and alerting out of the box, so I can catch and diagnose incidents without paying a SaaS observability bill or building my own telemetry stack from scratch."
riskiest_assumption: "We assume a 3-15 person team will accept operating its own observability infrastructure (upgrades, disk growth, backup, on-call for the stack itself) in exchange for not paying a SaaS bill — if that operational burden exceeds what the team can absorb alongside their actual product, they'll churn to a managed SaaS regardless of cost."
acceptance_criterion: "Given a fresh clone of uFawkesObs on a machine with Docker installed, when `make up` (or `docker compose --profile core up -d`) is run, then Grafana is reachable at localhost:3000 within 2 minutes with Prometheus, Loki, Tempo, and Alertmanager already wired as datasources and at least one pre-provisioned dashboard showing live data."
test_type: live-system
test_type_reasoning: "\"Ready to use within 2 minutes\" is a claim about the real compose stack converging to healthy and dashboards resolving live queries — no mock or unit test can stand in for actually starting the containers and observing Grafana render data."
dora_ai_capability: null
dora_core_capability: "Monitoring and Observability"
metric: "time_to_first_signal_minutes"
measurement_source: "manual (timed docker health polling against a genuine `git clone` of main, commit d2bff8c; note: `scripts/smoke-test.sh` referenced by the original draft of this field does not exist in the repo — no such script was ever added)"
baseline: "93s (1.55 min) from `make up` to all 7 core services healthy, with live Prometheus scrape data and 26 provisioned Grafana dashboards already present. PASS against the <2 minute target. Caveat: Docker images were already cached on the test machine from prior local work, so this excludes cold image-pull time, which is network-dependent and not controlled by this repo."
prior_art: "Grafana Cloud free tier, Datadog, SigNoz, OpenObserve — all viable alternatives for a small team. uFawkesObs's answer isn't a new telemetry backend, it's composing the same OSS components (Prometheus, Loki, Tempo, Grafana, OTel Collector, Alertmanager) that those vendors already build on, pre-wired and pre-provisioned, so a small team gets the vendor's default experience without the vendor's invoice."
status: ready-for-spec
retrospective: true
assumption_validated: true
---

# Discovery Brief: uFawkesObs (Product-Level)

> **Note on scope, stated plainly:** this brief was written after M2–M4 were
> already built, shipped, and merged. That inverts the entire point of a
> discovery gate — discovery is supposed to de-risk a decision *before*
> resources are committed, and nothing here changed a build decision, because
> the decisions were already made. Calling this "discovery" is generous; it is
> more accurately a **retrospective risk audit**: an attempt to make the user
> need and riskiest assumption behind the *already-existing* spec/design
> explicit and falsifiable, so that (a) M5 and future milestones get checked
> against a real JTBD instead of an assumed one, and (b) the gap this brief
> exposes — that the assumption below has never actually been tested — is
> visible instead of quietly absent. See "Honest Limitations of This Brief"
> below for what this document does *not* establish. Feature-level discovery
> briefs for individual increments belong in
> `docs/features/<feature-slug>/discovery-draft.md`, and for those, discovery
> should run *before* build — this repo already violates that order once;
> it shouldn't again.

## Job to Be Done

When I run a small (3-15 person) engineering team shipping on Docker Compose,
I want a self-hosted stack that gives me production-grade metrics, logs,
traces, and alerting out of the box, so I can catch and diagnose incidents
without paying a SaaS observability bill or building my own telemetry stack
from scratch.

This matches `README.md`'s stated audience directly: *"uFawkesObs is for
small-to-medium engineering teams (3–15 people) running Docker Compose
workloads who want production-grade metrics, logs, and traces without a SaaS
observability bill."*

## Riskiest Assumption

We assume a 3-15 person team will accept operating its own observability
infrastructure (upgrades, disk growth, backup, on-call for the stack itself)
in exchange for not paying a SaaS bill. If that operational burden exceeds
what the team can absorb alongside their actual product, they'll churn to a
managed SaaS regardless of cost — no amount of pre-provisioned dashboards
fixes an assumption that's wrong at the root.

This is the same risk `README.md`'s "What This Is Not" section already
gestures at ("Not horizontally scalable in this release — single-instance
only... Not multi-tenant") but doesn't state as a testable assumption. It's
also the reason `docs/KNOWN_LIMITATIONS.md` exists — every limitation listed
there is a place this assumption could break first.

## Acceptance Criterion

Given a fresh clone of uFawkesObs on a machine with Docker installed, when
`make up` (or `docker compose --profile core up -d`) is run, then Grafana is
reachable at `localhost:3000` within 2 minutes with Prometheus, Loki, Tempo,
and Alertmanager already wired as datasources and at least one pre-provisioned
dashboard showing live data.

`test_type: live-system` — "ready to use within 2 minutes" is a claim about
the real compose stack converging to healthy and dashboards resolving live
queries; no mock or unit test can stand in for actually starting the
containers and observing Grafana render data.

## DORA Outcome Target

- Capability: Monitoring and Observability (DORA Core Capability) — uFawkesObs
  is the substrate other planes (uFawkesPipe, uFawkesDevX, uFawkesDORA) build
  their own DORA Core Capability 6 (User-Centric Focus) and delivery metrics
  on top of; it doesn't measure its own AI capability directly.
- Metric: `time_to_first_signal_minutes` — wall-clock time from a fresh clone
  to a live, data-populated Grafana dashboard.
- Current baseline: **93s (1.55 min)**, measured 2026-08-10 against a genuine
  fresh clone — PASS against target. See `baseline` in frontmatter for method
  and caveats (image-cache warm, `scripts/smoke-test.sh` doesn't exist).
- Target: < 2 minutes (matches the acceptance criterion above).
- Measurement: manual timing today; a candidate future improvement is a real
  `scripts/smoke-test.sh` that emits its own duration so this becomes
  self-measuring rather than a one-off manual exercise.

## Prior Art

Grafana Cloud's free tier, Datadog, SigNoz, and OpenObserve all solve some
version of this problem already. uFawkesObs's answer isn't a new telemetry
backend — it composes the same OSS components those vendors build on
(Prometheus, Loki, Tempo, Grafana, OpenTelemetry Collector, Alertmanager),
pre-wired and pre-provisioned via Docker Compose, so a small team gets close
to the vendor's default experience without the vendor's invoice or the
multi-week integration effort of standing up each component by hand.

## Honest Limitations of This Brief

A candid read of this document, not a flattering one:

- **Retroactive, not gating.** This was written after M2–M4 shipped and
  merged. Real discovery would have run before that work started and could
  have changed its scope; this brief could not and did not. Treat it as an
  audit of the assumption already baked into the existing spec/design, not
  as evidence the assumption was validated before building on it.
- **The persona was inferred, not researched.** "solo-entrepreneur" (with
  `platform-engineer` as secondary) was derived from one sentence in
  `README.md`, not from user interviews, support tickets, GitHub issue
  patterns, or usage telemetry — because none of those currently exist for
  this repo. It's a reasonable placeholder read from the closest available
  evidence, not a researched finding. Don't cite it as if real users were
  consulted.
- **The riskiest assumption is named, not tested.** Stating "we assume a
  3-15 person team will accept the ops burden" is the easy half of
  discovery. No experiment has run to falsify it — there's no interview
  data, no churn signal, no adoption-vs-abandonment comparison. Until one of
  the experiments below runs, this assumption is a hypothesis, not a
  validated (or invalidated) finding.
- **The DORA-outcome mapping is a template fit, not a natural fit.**
  `time_to_first_signal_minutes` is an onboarding-friction metric. Mapping
  it to the DORA "Monitoring and Observability" core capability satisfies
  the discovery skill's required schema field, but this product's actual
  users (small teams evaluating whether to self-host observability) don't
  care about DORA taxonomy — they care about "will this work with minimal
  effort." Read the DORA mapping as bookkeeping for pipeline consistency
  across the uFawkes suite, not as a claim that DORA outcomes are what this
  particular decision turns on.

## Next Actual Discovery Experiment

What would make the riskiest assumption stop being a guess, ranked cheapest
first:

1. **Measure the acceptance criterion for real, now.** ✅ Done 2026-08-10 —
   93s against a genuine fresh clone, PASS against the <2 minute target. See
   `baseline` in frontmatter. Note: `scripts/smoke-test.sh` does not exist in
   the repo; the measurement used direct docker health polling instead. This
   validates the *onboarding-speed* sub-claim only — the deeper churn/
   operational-burden risk in `riskiest_assumption` is still open; see (2)
   and (3) below.
2. **Mine existing low-cost signal before running new experiments.** Check
   GitHub repo Insights (clone/traffic trends vs. stars, return-visitor
   rate) and scan open/closed issues for operational-burden complaints
   (disk growth, upgrade pain, "how do I back this up" questions). This is
   free, uses data that already exists, and would show early churn signal
   without needing to design a survey.
3. **If (1) and (2) don't settle it, ask directly.** Post a short
   discussion/issue template aimed at anyone who starred or forked the repo
   but never adopted it: "what stopped you?" A handful of real responses
   would outweigh everything in this brief.
4. Whichever of the above runs first should update `baseline` in this
   file's frontmatter and flip the riskiest assumption from "asserted" to
   either "supported" or "falsified" — don't let this brief go stale as a
   permanent hypothesis.

## Notes

- Secondary persona: the person actually running `make up` day-to-day is
  often closer to the `platform-engineer` persona (from the `discovery`
  skill's persona reference table) than a "solo-entrepreneur" in the
  literal sense — a designated platform/ops-minded engineer inside a
  3-15 person team, not necessarily its founder. The JTBD and acceptance
  criterion above hold either way; only the framing of "why this matters to
  the business" differs.
- This brief does not re-derive the full functional scope — that's
  `docs/product/spec.md` §4. It exists to answer *why* that scope was chosen,
  which the spec alone doesn't state.
- Known limitations that bear directly on the riskiest assumption (single-
  instance, no multi-tenancy, local filesystem storage only, no TLS between
  internal services) are already tracked in `docs/KNOWN_LIMITATIONS.md` —
  treat that file as the running list of ways this assumption could fail in
  practice, and revisit this brief if any of them get worse rather than
  better in a small-team deployment.
