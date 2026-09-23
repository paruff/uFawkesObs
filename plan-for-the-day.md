# Daily Plan: 2026-09-23

## 🎯 Primary Goal (`/goal`)

- **Focus:** PR-02 (#381) and PR-04 (#182) are the two remaining
  public-release blockers, and both are blocked on maintainer action
  (console access to the deploy host; a network-path decision for the
  rollback drill) — see `EXECUTION_QUEUE.md`'s "Unblock Runbook" for the
  exact steps. Neither is agent-executable today. Today's coding focus
  shifts to the highest-priority P2 item that *is* executable: #383.

---

## 🔁 Carryover (blocked on you, not today's coding focus)

- **Merge PR [#386](https://github.com/paruff/uFawkesObs/pull/386)** (require `GRAFANA_ADMIN_PASSWORD`, no default-admin fallback) and **PR [#392](https://github.com/paruff/uFawkesObs/pull/392)** (pin unit test deps for determinism) — both ready, awaiting your review.
- **#381** — deploy host presented 4 different SSH fingerprints across 4 attempts. Needs you at the host console. Runbook in `EXECUTION_QUEUE.md`.
- **#182** — rollback drill needs a network path from GitHub Actions to the LAN sandbox host (self-hosted runner / Tailscale / Cloudflare Tunnel). Runbook in `EXECUTION_QUEUE.md`.

---

## 📋 Today's Target (P2)

- [ ] **#383 — `find_repo_root()` hardcodes the checkout directory name.** *Acceptance Criteria:* `tests/unit/test_dora_event_schemas.py` passes regardless of the clone/worktree directory name (verified by running it from a differently-named path, not just `uFawkesObs`).

**Queued but not today** (each deserves its own session): #331 Rework Rate DORA alignment; #348 keep-or-delete decision on `docs/plan.md` (needs your call, not mine); extending the PR #392 lock-file pattern to the other five `requirements*.txt` files; SLO burn alerts + CFR-triggered rollback; HPA/VPA in the M5 Helm spec; River DSL vs OTel YAML ADR.

---

## ⚡ Execution Protocol

### 1. Test-Driven Development (`superpower:test-driven-development`)

#### #383 — repo-root detection portability

- [ ] **RED:** Reproduce in a worktree/clone not named `uFawkesObs` (e.g. `git worktree add /tmp/uFawkesObs-check2 <branch>`) — confirm `test_dora_event_schemas.py` fails there today.
- [ ] **GREEN:** Replace the `current.name == "uFawkesObs"` assertion in `find_repo_root()` with a marker-file walk (e.g. look for `compose.yaml` + `AGENTS.md` both present in a candidate directory) instead of matching the directory's own name.
- [ ] **REFACTOR:** Confirm the same helper isn't duplicated elsewhere in `tests/unit/` with the same hardcoded assumption.

### 2. Verification & Code Review (`request-code-review`)

- [ ] Run `pre-commit run --all-files` — all hooks pass
- [ ] Run `make test-unit` — unit tests pass, from both `uFawkesObs` and a differently-named path
- [ ] Review `git diff` against existing repository patterns

---

## 🧠 Session Retrospective (`ecc:learn`)

*(Fill in at end of session)*

- **Key Insights & Architecture:** [Patterns discovered, API decisions, or system behavior observed]
- **Edge Cases & Pitfalls:** [Unexpected issues, tool constraints, or debugging lessons]
- **Backlog Delta:** [New tasks, refactoring ideas, or technical debt to push to EXECUTION_QUEUE.md]

---

## 📊 Traceability

Every task traces up the cascade:

```
VISION.md (years) → MILESTONES.md (months) → EXECUTION_QUEUE.md (weeks) → plan-for-the-day.md (today)
```

| Today's Task | EXECUTION_QUEUE | MILESTONES | VISION Principle |
|---|---|---|---|
| #383 repo-root portability fix | P2 Next Sprint | H2 Late Beta / Public Release | Reproducible: works from any clone |
| #381 deploy host identity (carryover, blocked on you) | P0 This Week | H2 Late Beta / Public Release | GitOps Reconciliation |
| #182 rollback drill network path (carryover, blocked on you) | P0 This Week | H2 Late Beta / Public Release | GitOps Reconciliation |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
