# Daily Plan: 2026-09-24

## 🎯 Primary Goal (`/goal`)

- **Focus:** Finish the testing-pyramid rollout (#413-#417), then unblock
  the two remaining public-release blockers (#381, #182) now that the
  maintainer could provide direct NAS access (IP, hostname, Synology
  DS920+) instead of the console-only path `EXECUTION_QUEUE.md` previously
  assumed was required.

---

## ✅ Done Today

**Testing pyramid (#413-#417):**
- #413, #414 merged to `main` (Testcontainers spike, InSpec profile).
- #415: CI job added and merged; required-check wiring still pending
  (needs its false-positive rate confirmed over more real runs first).
- #416: Tempo and Loki integration tests migrated to Testcontainers
  (otel-collector spike already done) — 3 of ~8 files; rest tracked in
  `docs/TESTING_PYRAMID.md`'s checklist.
- #417: `tests/README.md` and `docs/DETERMINISM.md` updated, honestly
  marked partial since #416 isn't fully done.

**Other closed issues:**
- #359 — DORA acceptance test flakiness. Root cause found live: a fixed,
  reused `team_id` let stale Prometheus data from a prior local run
  satisfy the readiness poll instantly. Fixed with a per-run unique ID.
- #348 — deleted `docs/plan.md` (already self-declared superseded).
- #346 — finished migrating `docs/MODEL_POLICY.md` to be fully
  platform/provider-agnostic (no hardcoded model IDs or OpenCode-specific
  naming in the routing logic itself).
- Version bumped from alpha to beta (`0.4.0-beta.1`) — 6 of 7 `LB-*` exit
  criteria closed.

**Deploy pipeline (#381 / #393 / #182) — in progress, not yet closed:**
- Root cause found via live investigation, not assumed: every `deploy.yml`
  job ran on GitHub-hosted cloud runners, which have no route into the
  maintainer's home LAN at all. The "4 different SSH fingerprints"
  symptom is far better explained by an unstable public path (DDNS/port-
  forward) than host-key regeneration — confirmed on the actual NAS that
  `/etc/ssh/ssh_host_ed25519_key` has been unchanged since 2021.
- Registered a self-hosted GitHub Actions runner as a container on the
  deploy target itself (Synology DS920+), routed the four LAN-touching
  deploy jobs onto it (PR #456), and updated all four deploy secrets to
  the LAN path.
- Two more real bugs found and fixed on the first live deploy attempts:
  a stale `DEPLOY_PATH` repo variable pointing at a macOS dev path (fixed
  directly via `gh variable delete`), and a `make: command not found`
  failure — GNU Make isn't installed on this NAS at all, fixed by
  inlining `make up`'s two underlying commands (PR #457).
- **Not yet confirmed**: whether a full deploy run succeeds end-to-end
  now that #457 is merged. Acceptance Full was in progress for that merge
  commit as of this writing. Do not close #381/#393 until a run is seen
  fully green, and don't run the #182 rollback drill until #381 is closed
  (avoid drilling against a still-unstable path).

---

## 🔁 Carryover (next session)

- **Confirm the next full deploy run succeeds** — check
  `gh run list --repo paruff/uFawkesObs --workflow "GitOps Reconciliation Deploy" --branch main --limit 1`,
  and check the job logs show `synology-ds920` as the runner.
- **Close #381 and #393 together** once that's confirmed, with the run URL
  as evidence.
- **Run the #182 rollback drill** (`docs/ROLLBACK_DRILL.md` from
  Precondition 1) once #381 is closed.
- **#416 remaining files**: `test_grafana_integration.py`,
  `test_dashboards.py`/`test_alloy_and_dashboards.py` (cross-service,
  hardest — do last), rest of `test_otel_collector.py` /
  `test_prometheus_scraping.py`.
- **#415 required-check wiring**: add the InSpec conformance job to
  branch protection once its false-positive rate is confirmed low.
- **#417 full completion**: once #416 is fully done, re-audit
  `docs/DETERMINISM.md` again — the "not yet moot" conclusion from today
  may change once every `tests/integration/` file self-provisions.

**Queued but not today** (each deserves its own session): #331 Rework
Rate DORA alignment; #383 `find_repo_root()` portability; extending the
PR #392 lock-file pattern to the other five `requirements*.txt` files;
SLO burn alerts + CFR-triggered rollback; HPA/VPA in the M5 Helm spec;
River DSL vs OTel YAML ADR.

---

## 🧠 Session Retrospective (`ecc:learn`)

- **Key Insights & Architecture:** A squash-merge workflow strands any
  commit later merged into the now-stale feature branch instead of onto
  `main` directly — hit this with PRs #445/#446 stacked on already-merged
  #443/#444 branches; fixed by cherry-picking onto fresh branches off
  current `main`. Testcontainers' `wait=True` only confirms a container's
  port is listening, not that the service's own readiness check passes —
  cost a real flaky-test regression on Tempo before adding an explicit
  `/ready` poll. `docker context` can silently redirect the CLI to a
  different daemon (a stray `ssh://` context caused a confusing
  self-referential-SSH failure on the NAS). Bash's unquoted `~` and
  backticks-inside-double-quotes both bit us live during the deploy debug
  — always quote remote-command strings and heredoc commit messages.
- **Edge Cases & Pitfalls:** A GitHub Actions repo *variable* (not secret)
  can silently hold a stale value indefinitely — `DEPLOY_PATH` had a dead
  macOS path from Aug 31 that nothing ever caught until a live deploy
  attempt. Deploy scripts should assume the target host may lack tools
  the local dev Makefile assumes (`make` itself, in this case) — inlining
  the two underlying commands removed a dependency rather than adding one.
- **Backlog Delta:** None of today's findings need new backlog items
  beyond what's already tracked above — the deploy-pipeline work directly
  advances #381/#393/#182, which were already tracked.

---

## 📊 Traceability

```
VISION.md (years) → MILESTONES.md (months) → EXECUTION_QUEUE.md (weeks) → plan-for-the-day.md (today)
```

| Today's Work | EXECUTION_QUEUE | MILESTONES | VISION Principle |
|---|---|---|---|
| Testing pyramid #413-#417 | P2 Next Sprint | H2 Late Beta | Reliable confidence per commit |
| #359, #348, #346 (closed) | — | H2 Documentation Reconciliation | Reduce drift, keep tracker authoritative |
| Deploy pipeline #381/#393/#182 | P0 This Week | H2 Late Beta (LB-04) | GitOps Reconciliation |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
