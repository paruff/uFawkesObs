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

> **Status lives in GitHub, not here (2026-09-27).** This file holds priority
> tiers and goal definitions only: what each task is, why it matters, and how
> to verify it. Whether a task is done lives in its linked issue and in the
> [uFawkes Suite Release Project](https://github.com/users/paruff/projects/7).
> If you're looking for "is X done," check the issue.
>
> Why: the 2026-09-23 consolidation made this file the single status tracker,
> and it still drifted. Within four days it showed 9 completed items as
> pending (#331, #383, #334, #324, #352, #476, the guardrail eval, RG-6,
> RG-7). An issue's open/closed state can't drift from itself.
> `docs/PREPARE_FOR_PUBLIC_RELEASE.md` and `docs/PATH_TO_LATE_BETA.md` still
> define what the gates mean and their exit criteria.
>
> Every row links an issue. A goal with no issue isn't queued yet: file the
> issue first.

## Active Work (P0 — This Week)

| Task | Issue | Done when |
|---|---|---|
| Fix the deploy pipeline. The root cause was GitHub-hosted runners having no LAN route, not host-key regeneration. | [#381](https://github.com/paruff/uFawkesObs/issues/381) | A full deploy run succeeds end to end over the self-hosted runner |
| Recurring "Deploy (compose restart) failed" alert (a symptom of #381) | [#393](https://github.com/paruff/uFawkesObs/issues/393) | Closes together with #381 once a deploy run succeeds cleanly |
| Run and document a live rollback drill. Run it only after #381 closes, so it isn't run against an unstable deploy path. | [#182](https://github.com/paruff/uFawkesObs/issues/182) | `docs/ROLLBACK_DRILL.md` completed from Precondition 1 against the live host |

---

## Scheduled Work (P1 — This Sprint)

| Task | Issue | Done when |
|---|---|---|
| Bump alertmanager v0.28.0: 42 HIGH/CRITICAL fixable CVEs (found by `make scan-images`) | [#469](https://github.com/paruff/uFawkesObs/issues/469) | 0 fixable CRITICAL; old and new versions in the PR. Needs PM sign-off (image version). |
| The Validate Configs gate checks the Tempo config with 2.4.1, but the stack runs 2.10.5 | [#470](https://github.com/paruff/uFawkesObs/issues/470) | CI and `make validate-configs` use compose's exact images, derived rather than re-pinned. Needs PM sign-off (CI config). |
| Testcontainers fixtures join the shared `ufawkesobs` compose project and tear it down | [#471](https://github.com/paruff/uFawkesObs/issues/471) | Fixtures are isolated, and CI correctness no longer depends on step order. Blocks the dashboards step of #416. |
| Verify the devcontainer end to end (merged in #467) | [#499](https://github.com/paruff/uFawkesObs/issues/499) | A rebuild works, with Docker, Python 3.12, and the pinned tools; `make test` passes inside the container |

### Public-release goals (v1.0.0 milestone)

End-state goals with a verification command, so an agent can execute them
and a reviewer can check them. They add to the blockers in
[`docs/PREPARE_FOR_PUBLIC_RELEASE.md`](docs/PREPARE_FOR_PUBLIC_RELEASE.md)
rather than replace them. The full v1.0.0 bar is in
[`docs/ai-sdlc/v1.0.0/spec.md`](docs/ai-sdlc/v1.0.0/spec.md).

| ID | Goal (end state) | Issue | Verification |
|---|---|---|---|
| RG-1 | `make init && make up` on a clean machine reaches a healthy stack within 15 minutes, and Grafana shows metrics, logs **and** traces | [#494](https://github.com/paruff/uFawkesObs/issues/494) | A timed run following only the README Quick Start, plus a screenshot of each signal in Grafana |
| RG-2 | The README documents that DORA uses **SQLite by default** (no external database) | [#495](https://github.com/paruff/uFawkesObs/issues/495) | `grep -qi sqlite README.md` |
| RG-3 | A new user can follow the README Quick Start without maintainer help (after RG-1) | [#496](https://github.com/paruff/uFawkesObs/issues/496) | A walkthrough by someone who hasn't used the repo; gaps filed as issues |
| RG-4 | Each GitHub Release carries the changelog excerpt, a source tarball, and its SHA256 | [#497](https://github.com/paruff/uFawkesObs/issues/497) | `gh release view <tag> --json assets` lists the tarball and its `.sha256` |
| — | Upgrade notes from 0.4.x | [#498](https://github.com/paruff/uFawkesObs/issues/498) | Every contract-affecting change is listed, and the release notes link to it |

---

## Scheduled Work (P2 — Next Sprint)

| Task | Issue | Done when |
|---|---|---|
| Extend the dependency lock-file pattern (PR #392) to the remaining `requirements*.txt` | [#500](https://github.com/paruff/uFawkesObs/issues/500) | `tests/integration/`, `tests/acceptance/`, `dora/compute/`, `dora/ingestion/`, and `apps/telemetry-generator` all have lock files. Needs PM sign-off (dependencies). |
| Pin GitHub Actions runner images and exact Python patch versions (`docs/DETERMINISM.md` "Now" #3-4) | [#501](https://github.com/paruff/uFawkesObs/issues/501) | No `ubuntu-latest` left in `.github/workflows`. Needs PM sign-off (CI config). |
| Testing pyramid: wire InSpec in as a required check | [#415](https://github.com/paruff/uFawkesObs/issues/415) | The InSpec job is a required check on `main` |
| Testing pyramid: migrate the remaining integration tests to Testcontainers | [#416](https://github.com/paruff/uFawkesObs/issues/416) | Grafana, dashboards, and the rest migrated. Blocked on #471 for dashboards. |
| Testing pyramid: update the `tests/README.md` pyramid diagram | [#417](https://github.com/paruff/uFawkesObs/issues/417) | The diagram matches the landed state of #415 and #416 |
| SLO burn-rate alerts and rollback on change-failure-rate regression (expert feedback) | [#502](https://github.com/paruff/uFawkesObs/issues/502) | The acceptance suite includes a CFR-triggered rollback. Builds on #182. |
| Decide between Alloy River DSL and OTel YAML, and record it as an ADR (expert feedback) | [#503](https://github.com/paruff/uFawkesObs/issues/503) | An ADR records one chosen paradigm |
| Trim `AGENTS.md` to 150 lines or fewer, moving detail into `.claude/rules/` and skills | [#504](https://github.com/paruff/uFawkesObs/issues/504) | `wc -l AGENTS.md` is 150 or less, and every removed rule is still reachable |
| Skill descriptions state *when* to use each skill | [#505](https://github.com/paruff/uFawkesObs/issues/505) | A skill-routing eval passes |
| Rename the repo's `security-review` skill, which collides with the built-in `/security-review` | [#506](https://github.com/paruff/uFawkesObs/issues/506) | No duplicate skill names in a headless session's init event |
| Gate PRs on actionlint, hadolint, and trivy (a CI follow-up to #468) | [#474](https://github.com/paruff/uFawkesObs/issues/474) | Runs on relevant paths, at the same versions as `install-tools.sh`. Fix #469 and #472 first. Needs PM sign-off (CI config). |
| Exec-form CMD in the dora compute and ingestion Dockerfiles (hadolint DL3025) | [#472](https://github.com/paruff/uFawkesObs/issues/472) | `make lint-dockerfiles` is clean of DL3025, and `--profile dora stop` exits promptly |

> **Removed 2026-09-27:** "Add resource budgeting, HPA, VPA to M5 Helm chart
> spec". It contradicts `VISION.md`'s non-goal of Kubernetes-native
> deployment, and `docs/fawkes-migration.md`'s framing that Fawkes replaces
> uFawkesObs wholesale rather than hosting it. Kubernetes resource
> management belongs to the Fawkes track.

---

## Backlog (P3)

| Task | Issue | Notes |
|---|---|---|
| The Alertmanager `templates:` glob matches nothing | [#473](https://github.com/paruff/uFawkesObs/issues/473) | Harmless today, but named templates would silently fall back to defaults. It's also a v1.0.0 milestone candidate. |

---

## Recently Completed (for context, not re-tracked)

These were closed or merged by 2026-09-27 while this file still listed them
as pending. That drift is why status moved to GitHub:
- Issues #331 (Rework Rate), #383 (`find_repo_root`), #334 (Prometheus
  reload), #324 (dropped DORA events), and #352 (beta-pinned reusable
  workflow)
- PR #476, the AI-Native SDLC guardrails, which delivered **RG-6** (`.claude/`
  local files are git-ignored, re-verified with `git check-ignore` on
  2026-09-27) and **RG-7** (skills load in Claude Code)
- PR #489, the agent guardrail eval in CI
- **RG-5**, no secrets in git history (verified 2026-09-24)

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
