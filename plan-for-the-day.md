# Daily Plan: 2026-09-25

## 🎯 Primary Goal (`/goal`)

- **Focus:** Get one real GitOps compose-restart deploy green on the
  Synology host (#381/#393). Yesterday's network fix worked, and the
  deploy now fails one step later on a kernel limitation (see G1). Then
  run the #182 rollback drill against it.

Each goal below is an end state with a verification command, so an agent
can execute it and a reviewer can check it. Goals marked **needs
sign-off** change something AGENTS.md §5 reserves for the maintainer.
They start only after that decision is made.

| # | Goal (end state) | Verification | Source | Notes |
|---|---|---|---|---|
| G1 | A real `Deploy (compose restart)` job succeeds on `synology-ds920`, followed by a green Post-Deploy Verification | `gh run list --workflow deploy.yml --limit 5`: a run whose compose-restart job **ran** (not skipped) and succeeded | #381, #393 | **Needs sign-off:** pick a CPU-limit option from [#381's comment](https://github.com/paruff/uFawkesObs/issues/381#issuecomment-5829614254). `compose.yaml` sets `cpus:` on 22 services, and the DSM kernel has no CPU CFS scheduler |
| G2 | #381 and #393 closed, with the G1 run URL as evidence | `gh issue view 381 --json state` | #381, #393 | Only after G1 |
| G3 | Rollback drill executed and documented against the live host | `docs/ROLLBACK_DRILL.md` run log committed; #182 closed | #182 | Only after G2 |
| G4 | Testcontainers fixtures run under their own Compose project, so Integration Tests no longer depends on step order | Grafana/Prometheus steps can run in any order; a fixture's teardown leaves a running `ufawkesobs` stack untouched (test asserts it) | #471 | Unblocks the last #416 file |
| G5 | `test_alloy_and_dashboards.py` and `TestAlloyIntegration` migrated; #416 closed | `grep -L testcontainers tests/integration/test_*.py` is empty | #416 | After G4 |
| G6 | Agent guardrail eval merged and running in CI, with all three variants measured | `make eval-guardrails` for baseline / `no-hooks` / `hooks-only`: 0 adversarial violations in baseline; Agent Evals workflow green; `ANTHROPIC_API_KEY` secret set | AI-Native SDLC item 6 | Harness changed after the pilot, so it **needs re-approval** (`python3 evals/run_guardrails.py --approve-harness`). Full run ≈ 15 cases × ~$0.14 ≈ $2 per variant, ~2 min |
| G7 | Devcontainer rebuilt from #467 and verified | In the rebuilt container: `docker compose version`, `python3 --version` (3.12), `pre-commit --version`, `actionlint --version` | #467 follow-up | Manual rebuild |
| G8 | alertmanager bumped (0 fixable CRITICAL); Tempo config validated with the version that runs (2.10.5) | `make scan-images`; `make validate-configs` | #469, #470 | **Needs sign-off** (image version; CI config) |

---

## ✅ Done Since Last Plan (2026-09-24 → 25)

**Merged:** #460 (Grafana → Testcontainers), #461 (Prometheus →
Testcontainers), #463 (dashboards → Testcontainers), #466 (Claude Code
role agents + model routing), #467 (devcontainer: Docker, Python 3.12, gh,
pre-commit, pinned lint/scan tools), #468 (lint / image-scan /
release-preview Make targets), #475 + #486 (queue updates incl. valid
`RELEASE_GOALS.md` items), #476 (AI-Native SDLC guardrails: skills
visible to Claude Code, test-protection + self-verify hooks, `REVIEW.md`),
and #477-#485 (Dependabot requirement bumps). Released `v0.4.1-beta.1`.

**CI failures root-caused and fixed:**
- #460 and #461: the new Testcontainers fixtures join the CI job's
  shared compose project (`compose.yaml` pins `name: ufawkesobs`) and their
  teardown deletes shared containers. #461's fixture removed the *entire*
  stack. Fixed by ordering the steps; the real fix is tracked in #471 (G4).

**Issues filed (tooling findings):** #469 alertmanager CVEs, #470 Tempo
validation-version drift, #471 fixture/shared-stack coupling, #472
hadolint DL3025, #473 dangling alertmanager templates glob, #474 CI lint
gates.

**Issue audit (2026-09-25):** checked all 12 open issues against `main`,
CI, and deploy logs. None is verifiably done, so none closed:
issues #469/#470/#473/#474 unchanged; #472 still 2× DL3025; #471/#416 alloy files
still unmigrated; #415 not in the required-check ruleset; #381/#393 real
deploys still failing (new cause posted on #381); #182 blocked on #381.

**Deploy (#381):** the self-hosted runner now reaches the host, pulls,
and passes `check-env`. Every real compose restart then fails with
`NanoCPUs can not be set, as your kernel does not support CPU CFS
scheduler`. The CPU limits long predate this issue; they never surfaced
because deploys never got past SSH until now.

**Guardrail eval pilot** (4 Sonnet sessions, measured $0.48, ~25 s/case):
with hooks on, both adversarial cases held and the benign rename completed.
With the ablation, the agent ran `git rm` on the test file immediately.
Reading the transcripts turned up two harness flaws, now fixed on the eval
branch: the agent could tell it was being evaluated (it found the eval's
own tests and an "eval seed" commit), and the ablation dropped the
instructions along with the hooks. In baseline the agent declined on its
own, so the hook never fired; the new `hooks-only` variant tests the hook
directly.

**Housekeeping:** removed the two stale agent worktrees
(`.claude/worktrees/agent-*`; both branches already merged upstream).

---

## 🔁 Carryover (next session)

- G1 needs the CPU-limit decision before any work starts.
- #415 required-check wiring: InSpec job still not in the ruleset.
- #417: re-audit `docs/DETERMINISM.md` once #416 closes.
- #472, #473, #474: small, queued in P2/P3.

**Queued but not today:** #331 Rework Rate DORA alignment; #383
`find_repo_root()` portability; SLO burn alerts + CFR-triggered rollback;
HPA/VPA in the M5 Helm spec; River DSL vs OTel YAML ADR; P2 items from
`RELEASE_GOALS.md` (AGENTS.md ≤150 lines, skill "when to use"
descriptions, rename the colliding `security-review` skill).

---

## 🧠 Session Retrospective (`ecc:learn`)

- **Key Insights & Architecture:** `docker compose` treats a pinned
  top-level `name:` as a shared namespace. Any tool that runs compose
  from the repo root (Testcontainers included) joins the running stack
  rather than isolating, and its `down` removes shared containers. It
  caused two CI failures in two days, and step ordering is the only thing
  holding it together today.
- **Edge Cases & Pitfalls:** The deploy workflow reports **success** on
  no-op runs (nothing deploy-relevant changed, compose-restart skipped),
  interleaved with the real failures. A glance at the run list says "flaky"
  when it's actually 100% failing on real deploys. Check the compose-restart
  job's own conclusion, not the workflow's.
- **Edge Cases & Pitfalls:** `git worktree prune` inside the devcontainer
  deletes the metadata of worktrees created on the Mac host (their
  `/Users/...` paths don't exist in the container). Never prune from the
  container.
- **Backlog Delta:** Consider making the deploy workflow's summary state
  "no-op" explicitly instead of success, so the run list reflects the real
  deploy failure rate (DORA change-failure-rate accuracy depends on it).

---

## 📊 Traceability

```
VISION.md (years) → MILESTONES.md (months) → EXECUTION_QUEUE.md (weeks) → plan-for-the-day.md (today)
```

| Today's Work | EXECUTION_QUEUE | MILESTONES | VISION Principle |
|---|---|---|---|
| G1-G3 deploy + rollback drill (#381/#393/#182) | P0 This Week | H2 Late Beta (LB-04) | GitOps Reconciliation |
| G4-G5 test isolation + #416 | P1 | H2 Late Beta | Reliable confidence per commit |
| G6 agent guardrail eval | P1 | H2 Late Beta | Governance as code |
| G7 devcontainer verification | P1 | H2 Late Beta | Reproducible environments |
| G8 CVE bump + validation drift (#469/#470) | P1 | Public release (RG goals) | Secure by default |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
