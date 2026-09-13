# Daily Plan: 2026-09-13 (Afternoon)

## 🎯 Primary Goal (`/goal`)

- **Focus:** Verify H2 late-beta readiness; identify remaining gaps before public launch.

---

## 📋 Today's Target Issues

- [ ] **LB-04 Rollback Drill:** Verify sandbox host (Synology NAS 192.168.1.10) is reachable; run drill if possible — *Acceptance Criteria:* Drill completed over SSH, evidence captured in `docs/ROLLBACK_DRILL.md`
- [ ] **#357 Harden opencode agent:** Review current security posture; document gaps — *Acceptance Criteria:* Issue triaged with clear acceptance criteria for OIDC + egress policy
- [ ] **#335 LB-02 ports audit:** Verify all internal ports are localhost-bound — *Acceptance Criteria:* Audit complete, any gaps documented

---

## ⚡ Execution Protocol

### 1. Test-Driven Development (`superpower:test-driven-development`)

#### LB-04 — Rollback Drill

- [ ] **RED:** Check if Synology NAS is reachable (`ssh <host> "echo ok"`)
- [ ] **GREEN:** Run drill per `docs/ROLLBACK_DRILL.md` if reachable
- [ ] **REFACTOR:** Update `docs/PATH_TO_LATE_BETA.md` status when complete

#### #357 — Harden opencode agent

- [ ] **RED:** Review `.github/workflows/opencode.yml` for security gaps
- [ ] **GREEN:** Document gaps in issue comments
- [ ] **REFACTOR:** Create follow-up tasks if needed

#### #335 — LB-02 ports audit

- [ ] **RED:** Run `docker compose config | grep -A2 ports` to verify bindings
- [ ] **GREEN:** Document any non-localhost bindings
- [ ] **REFACTOR:** Create fix issue if gaps found

### 2. Verification & Code Review (`request-code-review`)

- [ ] Run `pre-commit run --all-files` — all hooks pass
- [ ] Run `make test-unit` — unit tests pass
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
| LB-04 Rollback Drill | P1 Active Beta Gates | H2 Late Beta | GitOps Reconciliation |
| #357 Harden agent | P1 Active Beta Gates | H2 Late Beta | Security First |
| #335 LB-02 ports | P2 Valuable, Not Urgent | H2 Late Beta | Security First |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
