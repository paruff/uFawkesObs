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

## Active Work (P0 — This Week)

*No P0 items currently. The stack is healthy and CI is green.*

---

## Scheduled Work (P1 — This Sprint)

### H2 Late Beta Gates

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| LB-04: Full rollback drill over SSH | [#182](https://github.com/paruff/uFawkesObs/issues/182) | Drill completed on sandbox host, evidence captured | 🟡 In Progress |
| Harden opencode agent (OIDC + egress) | [#357](https://github.com/paruff/uFawkesObs/issues/357) | Agent cannot execute tests without approval | 🔲 Pending |

### Documentation Reconciliation (All Done)

| Task | Source | Status | PR |
|---|---|---|---|
| Doc-reality sweep: classify aspirational markers | [#347](https://github.com/paruff/uFawkesObs/issues/347) | ✅ Done | #362 |
| Reconcile docs/plan.md status drift | [#348](https://github.com/paruff/uFawkesObs/issues/348) | ✅ Done | #362 |
| Document test pyramid and marker taxonomy | [#344](https://github.com/paruff/uFawkesObs/issues/344) | ✅ Done | #362 |
| Rename DAY ONE.md to docs/DAY_ONE.md | [#349](https://github.com/paruff/uFawkesObs/issues/349) | ✅ Done | #362 |
| Relocate top-level clutter | [#351](https://github.com/paruff/uFawkesObs/issues/351) | ✅ Done | #362 |
| Fix LB-04 status in PATH_TO_LATE_BETA.md | [#342](https://github.com/paruff/uFawkesObs/issues/342) | ✅ Done | #362 |
| Update MODEL_POLICY.md to grade-based system | [#346](https://github.com/paruff/uFawkesObs/issues/346) | ✅ Done | #362 |
| Consolidate opencode workflow files | [#350](https://github.com/paruff/uFawkesObs/issues/350) | ✅ Done | #362 |
| Update main-ci-guard to stable version | [#352](https://github.com/paruff/uFawkesObs/issues/352) | ✅ Done | #362 |
| Make DORA acceptance test deterministic | [#359](https://github.com/paruff/uFawkesObs/issues/359) | ✅ Done | #362 |
| Restructure README to ~150 lines | [#345](https://github.com/paruff/uFawkesObs/issues/345) | ✅ Done | #362 |
| Add test coverage measurement | [#343](https://github.com/paruff/uFawkesObs/issues/343) | ✅ Done | #362 |
| Close stale RELEASE_PLEASE_TOKEN issue | [#353](https://github.com/paruff/uFawkesObs/issues/353) | ✅ Done | Closed |

---

## Scheduled Work (P2 — Next Sprint)

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| Align Rework Rate with DORA definition | [#331](https://github.com/paruff/uFawkesObs/issues/331) | Metric uses deployment-derived calculation | 🔲 Pending |
| **Add SLO burn alerts + automated rollback on CFR regression** | Expert feedback | Acceptance suite includes CFR-triggered rollback | 🔲 Pending |
| **Add resource budgeting, HPA, VPA to M5 Helm chart spec** | Expert feedback | Helm chart includes HPA/VPA configs | 🔲 Pending |
| **Decide River DSL vs OTel YAML and document in ADR** | Expert feedback | Design decision documented, one paradigm chosen | 🔲 Pending |

---

---

## Backlog (P3)

| Task | Source | Notes |
|---|---|---|
| Prometheus /-/reload returns 200 without applying config | [#334](https://github.com/paruff/uFawkesObs/issues/334) | Silent failure; needs investigation |
| send-dora-deployment-event.sh drops failed events | [#324](https://github.com/paruff/uFawkesObs/issues/324) | Unpairs rollback recovery |
| LB-02: ports were only localhost-bound partially | [#335](https://github.com/paruff/uFawkesObs/issues/335) | Needs audit |

---

## Blocked Items

| Task | Blocked By | Resolution |
|---|---|---|
| LB-04 full drill | Need sandbox host (Synology NAS at 192.168.1.10 available) | Run drill on NAS |

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
