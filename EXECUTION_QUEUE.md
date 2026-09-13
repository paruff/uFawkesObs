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

### Documentation Reconciliation

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| Doc-reality sweep: classify aspirational markers in 5 docs files | [#347](https://github.com/paruff/uFawkesObs/issues/347) | Inventory produced, buckets agreed, stale markers fixed | ✅ Done |
| Reconcile docs/plan.md status drift against real issue state | [#348](https://github.com/paruff/uFawkesObs/issues/185) | All 21 referenced issues verified, statuses corrected | ✅ Done |
| Document test pyramid and marker taxonomy | [#344](https://github.com/paruff/uFawkesObs/issues/344) | tests/README.md exists with marker → workflow mapping | ✅ Done |
| Rename DAY ONE.md to docs/DAY_ONE.md | [#349](https://github.com/paruff/uFawkesObs/issues/349) | File moved, all relative links fixed, no broken references | ✅ Done |
| Relocate top-level clutter | [#351](https://github.com/paruff/uFawkesObs/issues/351) | AI_STANCE.md → docs/, docker-compose.integration.yml → config/ | ✅ Done |
| Fix LB-04 status in PATH_TO_LATE_BETA.md | [#342](https://github.com/paruff/uFawkesObs/issues/342) | Status matches ROLLBACK_DRILL.md reality | ✅ Done |

### Active Beta Gates

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| LB-04: Full rollback drill over SSH | [#182](https://github.com/paruff/uFawkesObs/issues/182) | Drill completed on sandbox host, evidence captured | 🟡 In Progress |
| Consolidate two opencode workflow files | [#350](https://github.com/paruff/uFawkesObs/issues/350) | Single workflow, no duplicate triggers | 🔲 Pending |
| Harden opencode agent (OIDC + egress) | [#357](https://github.com/paruff/uFawkesObs/issues/357) | Agent cannot execute tests without approval | 🔲 Pending |

---

## Scheduled Work (P2 — Next Sprint)

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| Release Please token missing in all repos | [#353](https://github.com/paruff/uFawkesObs/issues/353) | Token set, release automation working | 🔲 Pending |
| Required merge gate depends on beta workflow | [#352](https://github.com/paruff/uFawkesObs/issues/352) | Merge gate uses stable workflow version | 🔲 Pending |
| README restructure for public landing page | [#345](https://github.com/paruff/uFawkesObs/issues/345) | README < 200 lines, newcomer-friendly | 🔲 Pending |
| No test coverage measurement | [#343](https://github.com/paruff/uFawkesObs/issues/343) | Coverage report generated in CI | 🔲 Pending |
| MODEL_POLICY.md misaligned with OpenCode setup | [#346](https://github.com/paruff/uFawkesObs/issues/346) | Policy matches current tool routing | 🔲 Pending |
| Align Rework Rate with DORA definition | [#331](https://github.com/paruff/uFawkesObs/issues/331) | Metric uses deployment-derived calculation | 🔲 Pending |

---

## Backlog (P3)

| Task | Source | Notes |
|---|---|---|
| Prometheus /-/reload returns 200 without applying config | [#334](https://github.com/paruff/uFawkesObs/issues/334) | Silent failure; needs investigation |
| send-dora-deployment-event.sh drops failed events | [#324](https://github.com/paruff/uFawkesObs/issues/324) | Unpairs rollback recovery |
| LB-02: ports were only localhost-bound partially | [#335](https://github.com/paruff/uFawkesObs/issues/335) | Needs audit |
| Flaky test: local compute interval 240x CI's | [#359](https://github.com/paruff/uFawkesObs/issues/359) | Test environment mismatch |

---

## Blocked Items

| Task | Blocked By | Resolution |
|---|---|---|
| LB-04 full drill | Need sandbox host (Synology NAS at 192.168.1.10 available) | Run drill on NAS |
| RELEASE_PLEASE_TOKEN | Token not set in GitHub secrets | Manual token provisioning required |

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
