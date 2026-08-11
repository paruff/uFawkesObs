# Path to Late Beta — uFawkesObs

> Living document. "Late beta" is not yet a defined maturity stage anywhere
> else in this repo — this doc defines it and tracks progress toward it.
> Update status as issues close.

---

## Where We Are

Milestones M1–M4 are complete (`docs/product/spec.md`): core Compose stack,
repo hardening, cross-plane integration docs, and DORA/ecosystem wiring are
all shipped and tagged `v0.1.0`. `main` CI is green. This is effectively
**alpha** — internally dogfooded, functionally complete for the target
scope, but never validated against a real external adopter and with several
known gaps that would burn one on first contact.

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

| ID | Task | Issue | Status |
|----|------|-------|--------|
| LB-01 | Measure `time_to_first_signal_minutes` onboarding baseline | [#179](https://github.com/paruff/uFawkesObs/issues/179) | ✅ DONE (93s, PASS) |
| LB-02 | Restrict Loki/Tempo/Prometheus/Alertmanager ports to localhost by default | [#180](https://github.com/paruff/uFawkesObs/issues/180) | 🔲 PENDING |
| LB-03 | Add a tested Slack notification channel for Alertmanager | [#181](https://github.com/paruff/uFawkesObs/issues/181) | 🔲 PENDING |
| LB-04 | Run and document a live rollback drill | [#182](https://github.com/paruff/uFawkesObs/issues/182) | 🔲 PENDING (runbook ready) |
| LB-05 | Investigate GitOps Reconciliation Deploy transient failure | [#183](https://github.com/paruff/uFawkesObs/issues/183) | 🔲 PENDING |
| LB-06 | Add a beta feedback channel | [#184](https://github.com/paruff/uFawkesObs/issues/184) | 🔲 PENDING |
| LB-07 | Reconcile `docs/plan.md` status drift against real issue state | [#185](https://github.com/paruff/uFawkesObs/issues/185) | 🔲 PENDING |

All issues are labeled `late-beta` for tracking:
<https://github.com/paruff/uFawkesObs/issues?q=is%3Aissue+is%3Aopen+label%3Alate-beta>

> LB-04: the executable drill is in `docs/ROLLBACK_DRILL.md` and linked from
> `docs/DEPLOYMENT_STRATEGY.md`. The live run against a non-prod host is still
> PENDING. A suspected rollback-push gap (reusable-rollback `GITHUB_TOKEN`
> permissions / missing checkout) is tracked as a follow-up issue — the drill
> will confirm or refute it.

## Already Done (not re-tracked here)

- `scripts/check-env.sh` already fail-fasts on default/weak
  `GRAFANA_ADMIN_PASSWORD` — the "default credentials" gap in
  `docs/KNOWN_LIMITATIONS.md` is enforced, not just documented.
- PR #178 (merged) fixed Platform/Services dashboard variable plumbing that
  referenced nonexistent `cluster`/`namespace`/`environment` labels.

## Definition of Done

Late beta is reached when all seven issues above are closed and
`docs/KNOWN_LIMITATIONS.md` / `docs/DEPLOYMENT_STRATEGY.md` are updated to
reflect the new defaults. At that point, update this doc's status header and
announce readiness via the LB-06 feedback channel.
