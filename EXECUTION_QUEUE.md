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
| Merge: require `GRAFANA_ADMIN_PASSWORD`, no default-admin fallback | PR [#386](https://github.com/paruff/uFawkesObs/pull/386) | 🟡 Open, ready for review |
| Merge: pin unit test deps with a lock file (determinism) | PR [#392](https://github.com/paruff/uFawkesObs/pull/392) | 🟡 Open, ready for review |
| Deploy pipeline broken — host presented 4 different SSH fingerprints across 4 attempts | [#381](https://github.com/paruff/uFawkesObs/issues/381) | 🔴 **Blocked on you** — needs console access to the deploy host. Diagnostics + failure-alerting already shipped (PR #391, merged). **Exact steps: see "Unblock Runbook" below.** |
| Rollback drill can't run end-to-end — GitHub-hosted runners can't reach the LAN sandbox host | [#182](https://github.com/paruff/uFawkesObs/issues/182) | 🔴 **Blocked on you** — needs one infra decision (self-hosted runner / Tailscale / Cloudflare Tunnel). **Exact steps: see "Unblock Runbook" below.** |

---

## Unblock Runbook — #381 and #182

Both items below are the *only* two things standing between this repo and
public-release readiness (`docs/PREPARE_FOR_PUBLIC_RELEASE.md` PR-02/PR-04).
Neither can be advanced further by an agent — both need you at physical
hardware. This is the exact sequence.

### #381 — deploy host's SSH identity keeps changing

1. **Get physical/console access** to whatever `DEPLOY_HOST` points at — not
   over SSH (that's the channel in question), the actual console/screen, or
   a management interface you trust independently (IPMI, Synology DSM web
   UI on the LAN, etc.).
2. **Read the host's real current fingerprint at the console:**
   ```bash
   ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
   ```
3. **Check whether host keys persist across restarts** — this is the likely
   root cause:
   ```bash
   ls -la /etc/ssh/ssh_host_ed25519_key
   ```
   If the file's mtime lines up with the host's last boot/restart time,
   `/etc/ssh` isn't on persistent storage (common on containers, some NAS
   OS images, or after an OS reinstall) and regenerates keys every restart.
   **Fix that first** — move `/etc/ssh` host keys to a persistent volume —
   before touching the GitHub secret, or you'll be back here after the next
   restart.
4. **Confirm `DEPLOY_HOST` itself is stable** — check the value you
   originally set in GitHub → Settings → Secrets and variables → Actions →
   `DEPLOY_HOST` (you can see it was set, not read it back) and confirm it's
   not a dynamic-DNS name that could resolve to a different machine over
   time.
5. **Once you're confident the key is genuine and will stay stable**, get it
   in the exact format the secret needs:
   ```bash
   ssh-keyscan -t ed25519 <the-host>
   ```
6. **Update the secret:**
   ```bash
   gh secret set DEPLOY_HOST_KEY --repo paruff/uFawkesObs
   # paste the ssh-keyscan output line, Ctrl-D
   ```
7. **Re-run the deploy** (merge any PR, or re-run the last failed
   `deploy.yml` run from the Actions tab) and confirm it connects.
8. **If it fails again with yet another different fingerprint**, stop —
   that confirms the target itself is changing, not just its host keys.
   Don't re-pin again; investigate DNS/network routing to `DEPLOY_HOST`
   instead. PR #391's diagnostic step logs the resolved IP each run now, so
   compare that across the next few runs.

### #182 — rollback drill needs a network path

`docs/ROLLBACK_DRILL.md` §0a already lays out the decision and preference
order — this is the condensed version:

1. **Pick one:**
   - **Self-hosted runner on the LAN (recommended)** — register a GitHub
     Actions runner directly on the Synology NAS (or any always-on LAN
     box): repo → Settings → Actions → Runners → New self-hosted runner,
     follow the registration script it gives you. Nothing inbound exposed;
     the SSH hop becomes local to that machine.
   - **Tailscale/WireGuard** — join the NAS and (for the drill) a runner to
     the same tailnet; no inbound firewall changes.
   - **Cloudflare Tunnel** — works, but adds a dependency in the exact path
     the drill exists to test.
   - Avoid port-forwarding SSH from the internet (§0a explains why).
2. **Point the drill at it:** update the `DEPLOY_PATH` repo variable and the
   `DEPLOY_HOST`/`DEPLOY_USER`/`DEPLOY_KEY`/`DEPLOY_HOST_KEY` secrets to the
   sandbox host, not the maintainer workstation they point at today.
3. **Run `docs/ROLLBACK_DRILL.md` from Precondition 1 onward** — the
   procedure itself is already written and ready; it was only ever blocked
   on step 1.
4. **Record the result** in that doc's "Drill Results" section, then close
   [#182](https://github.com/paruff/uFawkesObs/issues/182).

---

## Scheduled Work (P1 — This Sprint)

*No P1 items currently — the last one (#357, opencode agent hardening) closed via PR #371, merged.*

---

## Scheduled Work (P2 — Next Sprint)

| Task | Source | Acceptance Criteria | Status |
|---|---|---|---|
| Align Rework Rate with DORA definition | [#331](https://github.com/paruff/uFawkesObs/issues/331) | Metric uses deployment-derived calculation | 🔲 Pending |
| `find_repo_root()` hardcodes checkout dir name `uFawkesObs` | [#383](https://github.com/paruff/uFawkesObs/issues/383) | Test passes from any clone/worktree name | 🔲 Pending |
| Should `docs/plan.md` be deleted? | [#348](https://github.com/paruff/uFawkesObs/issues/348) | Maintainer decides keep-with-owner or delete | 🔲 Pending — mechanical reconciliation done, this is the one open question |
| Extend dependency lock-file pattern (PR #392) to remaining `requirements*.txt` | Follow-up to #392, see [`docs/DETERMINISM.md`](docs/DETERMINISM.md) | `tests/integration/`, `tests/acceptance/`, `dora/compute/`, `dora/ingestion/`, `apps/telemetry-generator` all get lock files | 🔲 Pending |
| Pin GitHub Actions runner images (`ubuntu-latest` → e.g. `ubuntu-24.04`) and exact Python patch versions | [`docs/DETERMINISM.md`](docs/DETERMINISM.md) "Now" #3-4 | 22 workflow occurrences pinned; needs PM sign-off (AGENTS.md §5, CI/CD config) | 🔲 Pending — awaiting sign-off |
| Testing pyramid: Testcontainers + InSpec | [`docs/TESTING_PYRAMID.md`](docs/TESTING_PYRAMID.md), issues [#413](https://github.com/paruff/uFawkesObs/issues/413)-[#417](https://github.com/paruff/uFawkesObs/issues/417) | 5-issue rollout: spike → InSpec profile → CI-gate it → full migration → docs update | 🔲 Pending |
| **Add SLO burn alerts + automated rollback on CFR regression** | Expert feedback | Acceptance suite includes CFR-triggered rollback | 🔲 Pending |
| **Add resource budgeting, HPA, VPA to M5 Helm chart spec** | Expert feedback | Helm chart includes HPA/VPA configs | 🔲 Pending |
| **Decide River DSL vs OTel YAML and document in ADR** | Expert feedback | Design decision documented, one paradigm chosen | 🔲 Pending |

---

## Backlog (P3)

| Task | Source | Notes |
|---|---|---|
| Prometheus /-/reload returns 200 without applying config | [#334](https://github.com/paruff/uFawkesObs/issues/334) | Silent failure; needs investigation |
| send-dora-deployment-event.sh drops failed events | [#324](https://github.com/paruff/uFawkesObs/issues/324) | Unpairs rollback recovery |
| `paruff/ufawkespipe` reusable workflows pinned to a beta tag | [#352](https://github.com/paruff/uFawkesObs/issues/352) | Merge gate depends on `@v1.4.0-beta.1`/`@v1.2.0`, not a stable release |

---

## Recently Completed (for context, not re-tracked)

Public-release blockers PR-01/PR-03 (Grafana anonymous access, internal port
exposure) and the README restructure / stranded coverage-measurement fix —
see git log or the closed issues (#380, #335, #345, #343) rather than a
status table here, so this doesn't drift again.

---

## Blocked Items

**#381** (deploy host identity unstable) and **#182** (rollback drill needs
a network path) — both blocked on maintainer action, not agent-executable.
See the Unblock Runbook above for the exact steps on each.

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
