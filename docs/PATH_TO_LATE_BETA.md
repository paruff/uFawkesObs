# Path to Late Beta — uFawkesObs

> Living document. "Late beta" is not yet a defined maturity stage anywhere
> else in this repo — this doc defines it and tracks progress toward it.
> Update status as issues close.

---

## Where We Are

Milestones M1–M4 are complete (`docs/product/spec.md`): core Compose stack,
repo hardening, cross-plane integration docs, and DORA/ecosystem wiring are
all shipped and tagged `v0.1.0`. `main` CI is green.

**As of the `0.4.0-beta.1` release, versioning moved from alpha to beta**:
six of the seven `LB-*` exit criteria below are closed. The one remaining
gate, LB-04 (a live rollback drill), is blocked on infrastructure access
the maintainer needs to arrange (see `EXECUTION_QUEUE.md`'s Unblock
Runbook) — not on outstanding feature work. Per `docs/RELEASE_PROCESS.md`,
releases stay marked as GitHub prereleases (`"prerelease": true`) until
LB-04 also closes and "late beta" is formally reached; the alpha→beta move
is a maturity-label update, not a claim that every exit criterion here is
met yet.

## What "Late Beta" Means Here

Per `docs/product/discovery-draft.md`, the target user is a 3–15 person
engineering team running Docker Compose who wants production-grade metrics,
logs, traces, and alerting without a SaaS bill. **Late beta means that team
can clone the repo, run `make up`, and rely on it for real (non-production)
use with reasonable confidence** — not that uFawkesObs is production-hardened
or multi-tenant.

Concretely, late beta requires:

1. The onboarding promise is *measured*, not assumed (LB-01).
2. The stack doesn't leak telemetry data by default when run on a shared or
   cloud host, not just a laptop (LB-02).
3. An alert actually reaches a human somewhere (LB-03).
4. Rollback has been proven to work, not just documented (LB-04).
5. The deploy pipeline itself is stable — no known flakiness (LB-05).
6. Beta adopters have a real way to report friction back (LB-06).
7. The backlog they'd land on to contribute is trustworthy, not stale
   (LB-07).

## Explicitly Out of Scope for Late Beta

- **M5 — Kubernetes/Helm deployment** (`v2.0.0` per `docs/product/spec.md`,
  issues #84–#87). The target persona ships on Docker Compose; Kubernetes
  support is a separate, later milestone for a different audience.
- **Multi-host progressive delivery** (canary/staging/load-balanced
  production, per `docs/DEPLOYMENT_STRATEGY.md`'s "Target Model"). That's
  production-hardening for when uFawkesObs serves real production traffic,
  which is explicitly a future gate, not a beta requirement.
- **TLS between internal services, object storage backends, HA** — all
  listed in `docs/KNOWN_LIMITATIONS.md` as intentional gaps for a
  single-host local-dev/eval deployment. Still out of scope for beta.

## Exit Criteria

> **Live status lives in [`EXECUTION_QUEUE.md`](../EXECUTION_QUEUE.md) now**,
> not here — this table used to carry its own status and drifted from the
> queue (e.g. LB-04 was marked "just needs scheduling" here after the queue
> had already found the harder blocker). This table defines *what each gate
> requires*; go to the queue for *is it done*.

| ID | Task | Issue |
|----|------|-------|
| LB-01 | Measure `time_to_first_signal_minutes` onboarding baseline | [#179](https://github.com/paruff/uFawkesObs/issues/179) |
| LB-02 | Restrict Loki/Tempo/Prometheus/Alertmanager ports to localhost by default | [#180](https://github.com/paruff/uFawkesObs/issues/180) (follow-up: [#335](https://github.com/paruff/uFawkesObs/issues/335)) |
| LB-03 | Add a tested Slack notification channel for Alertmanager | [#181](https://github.com/paruff/uFawkesObs/issues/181) |
| LB-04 | Run and document a live rollback drill | [#182](https://github.com/paruff/uFawkesObs/issues/182) — see `docs/ROLLBACK_DRILL.md` for the procedure |
| LB-05 | Investigate GitOps Reconciliation Deploy transient failure | [#183](https://github.com/paruff/uFawkesObs/issues/183) |
| LB-06 | Add a beta feedback channel | [#184](https://github.com/paruff/uFawkesObs/issues/184) |
| LB-07 | Reconcile `docs/plan.md` status drift against real issue state | [#185](https://github.com/paruff/uFawkesObs/issues/185), ongoing via [#348](https://github.com/paruff/uFawkesObs/issues/348) |

All issues are labeled `late-beta` for tracking:
<https://github.com/paruff/uFawkesObs/issues?q=is%3Aissue+is%3Aopen+label%3Alate-beta>

## Definition of Done

Late beta is reached when all seven issues above are closed (see
`EXECUTION_QUEUE.md` for current status) and `docs/KNOWN_LIMITATIONS.md` /
`docs/DEPLOYMENT_STRATEGY.md` are updated to reflect the new defaults. At
that point, update this doc's status header and announce readiness via the
LB-06 feedback channel.

## How This Connects

See also [`PREPARE_FOR_PUBLIC_RELEASE.md`](PREPARE_FOR_PUBLIC_RELEASE.md) —
a separate readiness bar for a stranger cloning the repo with no maintainer
present, as opposed to a trusted team relying on it for real.

This document is part of the H2 horizon in [`../MILESTONES.md`](../MILESTONES.md). Each LB-## task feeds into the planning cascade:

```
VISION.md (years) → MILESTONES.md (months) → EXECUTION_QUEUE.md (weeks) → plan-for-the-day.md (today)
```

LB-## tasks that are ✅ DONE are checked off in `MILESTONES.md` § H2. Tasks that are 🔲 PENDING appear in `EXECUTION_QUEUE.md` as scheduled work.
