# Daily Plan: 2026-09-14

## 🎯 Primary Goal (`/goal`)

- **Focus:** P1 gates are in progress, not blocked — shift today's new work to P2 (`EXECUTION_QUEUE.md` "Scheduled Work (P2)").

---

## 🔁 P1 Carryover (in progress, not today's focus)

- **LB-04 Rollback Drill** ([#182](https://github.com/paruff/uFawkesObs/issues/182)) — Synology NAS (192.168.1.10) confirmed reachable over SSH 2026-09-14. The drill itself (induce failure → confirm → recover per `docs/ROLLBACK_DRILL.md`) is a live-infra operation deliberately deferred to a session with room to run it carefully end to end.
- **#357 Harden opencode agent** — interim `bash:deny` fix open in [PR #371](https://github.com/paruff/uFawkesObs/pull/371), pending your review/merge. OIDC token exchange + `step-security/harden-runner` egress-policy still open behind it.

---

## 📋 Today's Target (P2)

- [ ] **#331 Align Rework Rate with DORA definition** — *Acceptance Criteria:* Metric uses deployment-derived calculation, not the current definition.
- [ ] **#335 LB-02 ports — decision needed:** Audit was re-verified and posted 2026-09-14 ([comment](https://github.com/paruff/uFawkesObs/issues/335#issuecomment-5662905261)). Per AGENTS.md §5, closing any port requires your sign-off — this is a decision to bring to you, not an agent-executable task. Candidates to close: `8888`/`8889` (otel-collector, internal-scrape-only), `9095`/`9096` (tempo/loki grpc), `9100` (node-exporter), `12345` (alloy UI, unauthenticated), `14250`/`14268`/`9411` (jaeger/zipkin receivers, only needed if something sends those formats).

**Queued but not today** (larger design/spec work, each deserves its own session): SLO burn alerts + automated rollback on CFR regression; resource budgeting/HPA/VPA in the M5 Helm chart spec; River DSL vs OTel YAML ADR decision.

---

## ⚡ Execution Protocol

### 1. Test-Driven Development (`superpower:test-driven-development`)

#### #331 — Rework Rate DORA alignment

- [ ] **RED:** Locate current Rework Rate calculation; write a failing test asserting deployment-derived semantics (matches DORA's definition: failed deployments requiring a fix / total deployments — not the current basis).
- [ ] **GREEN:** Implement the deployment-derived calculation to pass the test.
- [ ] **REFACTOR:** Update any dashboards/docs referencing the old definition.

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
| #331 Rework Rate alignment | P2 Next Sprint | H2 Late Beta | Deployment-derived DORA metrics |
| #335 LB-02 ports decision | P2 Next Sprint | H2 Late Beta | Security First |
| LB-04 Rollback Drill (carryover) | P1 This Sprint | H2 Late Beta | GitOps Reconciliation |
| #357 Harden agent (carryover) | P1 This Sprint | H2 Late Beta | Security First |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
