# EXECUTION_QUEUE.md — uFawkesObs

> **Horizon:** Weeks | **Owner:** Maintainer | **Review:** Weekly
> **Feeds into:** [`MILESTONES.md`](MILESTONES.md) ← source | [`plan-for-the-day.md`](plan-for-the-day.md) → next tier

---

## Priority Tiers

| Tier | Meaning | Action |
|---|---|---|
| **P0** | Blocks release or breaks existing functionality | Work on this first |
| **P1** | High-value, aligned with active milestone | Schedule this week |
| **P2** | Valuable but not urgent | Next sprint |
| **P3** | Nice-to-have, low priority | Backlog |

---

> **Consolidation note (2026-09-23):** `docs/PREPARE_FOR_PUBLIC_RELEASE.md` and
> `docs/PATH_TO_LATE_BETA.md` used to each carry their own live status table,
> which drifted from each other and from here (e.g. this file claimed the
> LB-04 drill "just needs scheduling" while the actual doc said the harder
> GitHub-Actions-to-LAN network problem was still unsolved). Those two docs
> now define *what the gates mean and their exit criteria only* — this file
> is the single place tracking current task status. If you're looking for
> "is X done," look here, not there.

## Active Work (P0 — This Week)

| Task | Source | Status |
|---|---|---|
| Fix deploy pipeline — root cause was GitHub-hosted runners having no LAN route, not host-key regeneration | [#381](https://github.com/paruff/uFawkesObs/issues/381) | 🟡 **In progress, verification pending.** Self-hosted runner registered on the deploy target (Synology DS920+), `DEPLOY_HOST`/`DEPLOY_USER`/`DEPLOY_HOST_KEY`/`DEPLOY_KEY` updated to the LAN path (PR [#456](https://github.com/paruff/uFawkesObs/pull/456), merged), a stale `DEPLOY_PATH` repo variable fixed live, and a `make`-not-installed failure fixed (PR [#457](https://github.com/paruff/uFawkesObs/pull/457), merged). Waiting on the next full deploy run (triggered by #457's own merge) to confirm end-to-end success before closing. |
| Recurring "Deploy (compose restart) failed" alert | [#393](https://github.com/paruff/uFawkesObs/issues/393) | 🟡 Symptom of #381 — close together once a deploy run succeeds cleanly. |
| Rollback drill can't run end-to-end — GitHub-hosted runners can't reach the LAN sandbox host | [#182](https://github.com/paruff/uFawkesObs/issues/182) | 🟡 **Network path now exists** (same self-hosted runner as #381) — the actual drill (`docs/ROLLBACK_DRILL.md` from Precondition 1) hasn't been run yet. Do this once #381 is confirmed closed, so the drill isn't run against a still-unstable deploy path. |

---

## Scheduled Work (P1 — This Sprint)

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| Bump alertmanager v0.28.0 — 42 HIGH/CRITICAL fixable CVEs (found by `make scan-images`) | [#469](https://github.com/paruff/uFawkesObs/issues/469) | 0 fixable CRITICAL; old/new versions in PR; needs PM sign-off (image version) | 🔲 Pending — awaiting sign-off |
| Validate Configs gate checks Tempo config with 2.4.1, stack runs 2.10.5 | [#470](https://github.com/paruff/uFawkesObs/issues/470) | CI + `make validate-configs` use compose's exact images, derived not re-pinned; needs PM sign-off (CI config) | 🔲 Pending — awaiting sign-off |
| Testcontainers fixtures join the shared `ufawkesobs` compose project and tear it down | [#471](https://github.com/paruff/uFawkesObs/issues/471) | Fixtures isolated; CI correctness no longer depends on step order. Blocks the dashboards step of #416 below | 🔲 Pending |
| Review + merge dev tooling PRs: Claude Code agents, devcontainer, lint/scan targets | [#466](https://github.com/paruff/uFawkesObs/pull/466), [#467](https://github.com/paruff/uFawkesObs/pull/467), [#468](https://github.com/paruff/uFawkesObs/pull/468) | #467: rebuild the devcontainer from the new definition and confirm Docker + Python work end-to-end | 🟡 In review |

---

## Scheduled Work (P2 — Next Sprint)

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| Align Rework Rate with DORA definition | [#331](https://github.com/paruff/uFawkesObs/issues/331) | Metric uses deployment-derived calculation | 🔲 Pending |
| `find_repo_root()` hardcodes checkout dir name `uFawkesObs` | [#383](https://github.com/paruff/uFawkesObs/issues/383) | Test passes from any clone/worktree name | 🔲 Pending |
| Extend dependency lock-file pattern (PR #392) to remaining `requirements*.txt` | Follow-up to #392, see [`docs/DETERMINISM.md`](docs/DETERMINISM.md) | `tests/integration/`, `tests/acceptance/`, `dora/compute/`, `dora/ingestion/`, `apps/telemetry-generator` all get lock files | 🔲 Pending |
| Pin GitHub Actions runner images (`ubuntu-latest` → e.g. `ubuntu-24.04`) and exact Python patch versions | [`docs/DETERMINISM.md`](docs/DETERMINISM.md) "Now" #3-4 | 22 workflow occurrences pinned; needs PM sign-off (AGENTS.md §5, CI/CD config) | 🔲 Pending — awaiting sign-off |
| Testing pyramid: Testcontainers + InSpec | [`docs/TESTING_PYRAMID.md`](docs/TESTING_PYRAMID.md) | #413/#414 done (on `main`); #415's CI job done, required-check wiring still pending; #416 partial (otel-collector, Tempo, Loki migrated, Grafana/dashboards/rest remain); #417 partial (docs updated, marked honest-in-progress) | 🟡 In progress |
| **Add SLO burn alerts + automated rollback on CFR regression** | Expert feedback | Acceptance suite includes CFR-triggered rollback | 🔲 Pending |
| **Add resource budgeting, HPA, VPA to M5 Helm chart spec** | Expert feedback | Helm chart includes HPA/VPA configs | 🔲 Pending |
| **Decide River DSL vs OTel YAML and document in ADR** | Expert feedback | Design decision documented, one paradigm chosen | 🔲 Pending |
| Gate PRs on actionlint, hadolint, trivy (CI follow-up to #468) | [#474](https://github.com/paruff/uFawkesObs/issues/474) | Runs on relevant paths, same versions as `install-tools.sh`; fix #469/#472 first; needs PM sign-off (CI config) | 🔲 Pending — after #468 |
| Exec-form CMD in dora compute/ingestion Dockerfiles (hadolint DL3025) | [#472](https://github.com/paruff/uFawkesObs/issues/472) | `make lint-dockerfiles` clean of DL3025; `--profile dora stop` exits promptly | 🔲 Pending |

---

## Backlog (P3)

| Task | Source | Notes |
|---|---|---|
| Prometheus /-/reload returns 200 without applying config | [#334](https://github.com/paruff/uFawkesObs/issues/334) | Silent failure; needs investigation |
| send-dora-deployment-event.sh drops failed events | [#324](https://github.com/paruff/uFawkesObs/issues/324) | Unpairs rollback recovery |
| `paruff/ufawkespipe` reusable workflows pinned to a beta tag | [#352](https://github.com/paruff/uFawkesObs/issues/352) | Merge gate depends on `@v1.4.0-beta.1`/`@v1.2.0`, not a stable release |
| Alertmanager `templates:` glob matches nothing | [#473](https://github.com/paruff/uFawkesObs/issues/473) | Harmless today; named templates would silently fall back to defaults |

---

## Recently Completed (for context, not re-tracked)

Public-release blockers PR-01/PR-03 (Grafana anonymous access, internal port
exposure) and the README restructure / stranded coverage-measurement fix —
see git log or the closed issues (#380, #335, #345, #343) rather than a
status table here, so this doesn't drift again.

`docs/plan.md` deleted (#348) — the tracker (this file, `MILESTONES.md`,
`EXECUTION_QUEUE.md`) is now the sole source of truth for planning status,
removing the recurring reconciliation cost that made #348/LB-07 necessary
in the first place.

DORA acceptance test flakiness (#359) fixed — root cause was a fixed,
reused `team_id` letting a stale Prometheus series from an earlier local
run satisfy the readiness poll instantly instead of waiting for the
current run's own event; confirmed live, not just reasoned about.

`MODEL_POLICY.md` migrated to platform/provider-agnostic (#346) — no more
hardcoded model IDs or OpenCode-specific product names in the routing logic
itself, only benchmark thresholds and dispatch-mode properties.

Project status moved from alpha to beta (`0.4.0-beta.1`) — 6 of 7 `LB-*`
exit criteria closed; only LB-04 (#182) remains, now unblocked (network
path exists) but not yet run.

---

## How Tasks Flow

```
VISION.md (years)
    ↓ "What principles guide us?"
MILESTONES.md (months)
    ↓ "What milestone are we working on?"
EXECUTION_QUEUE.md (weeks) ← you are here
    ↓ "What specific tasks are ready?"
plan-for-the-day.md (today)
    ↓ "What am I doing right now?"
```

**Scope Drift Protection:** Before adding a task to this queue, check it against VISION.md non-goals. If it violates core principles, it gets rejected before reaching daily work.

**Bottom-Up Feedback:** Learnings from `plan-for-the-day.md` (session learnings, newly discovered tech debt) route back here for reprioritization.

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| **EXECUTION_QUEUE.md** (this file) | Weeks | What specific tasks are ready to be worked? |
| [`plan-for-the-day.md`](plan-for-the-day.md) | Today | What am I doing right now? |
