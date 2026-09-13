# Daily Plan: 2026-09-13

## 🎯 Primary Goal (`/goal`)

- **Focus:** Close P1 documentation and CI cleanup items to clear the path toward H2 late-beta readiness.

---

## 📋 Open Issue Inventory

### P0 — Release Blockers

| Issue | Title | Labels | Status |
|---|---|---|---|
| #353 | RELEASE_PLEASE_TOKEN missing in all five repos | `release-blocker` | 🔲 Blocked (requires manual GitHub secret provisioning) |

### P1 — High Value, Aligned with H2 Late Beta

| Issue | Title | Labels | Status |
|---|---|---|---|
| #350 | Consolidate the two opencode workflow files | `enhancement` | ⬜ Ready |
| #352 | Required merge gate depends on a beta-tagged reusable workflow | `enhancement` | ⬜ Ready |
| #346 | MODEL_POLICY.md describes a Copilot ladder that no longer matches the OpenCode setup | `documentation` | ⬜ Ready |
| #359 | Flaky test: local compute interval is 240x CI's | `bug` | ⬜ Ready |
| #345 | README is 602 lines — restructure for a public landing page | `documentation` | ⬜ Ready |
| #343 | No test coverage measurement despite an 80% mandate | `enhancement` | ⬜ Ready |

### P2 — Valuable, Not Urgent

| Issue | Title | Labels | Status |
|---|---|---|---|
| #335 | LB-02 is recorded as done, but only the HTTP ports were localhost-bound | — | ⬜ Ready |
| #334 | Prometheus /-/reload returns 200 without applying the new config | — | ⬜ Ready |
| #331 | Align Rework Rate with DORA's actual (deployment-derived) definition | — | ⬜ Ready |
| #324 | send-dora-deployment-event.sh silently drops failed events | — | ⬜ Ready |
| #357 | Harden the opencode agent before allowing test execution | `enhancement` | ⬜ Ready |

### Already Resolved (in PR #362)

| Issue | Title | Resolution |
|---|---|---|
| #342 | LB-04 status in PATH_TO_LATE_BETA contradicts ROLLBACK_DRILL.md | ✅ Fixed |
| #344 | Document the test pyramid and marker taxonomy | ✅ Created tests/README.md |
| #347 | Doc-reality sweep: aspirational and TODO markers | ✅ Created inventory |
| #348 | Reconcile docs/plan.md status drift | ✅ Reconciled |
| #349 | Rename DAY ONE.md to docs/DAY_ONE.md | ✅ Renamed |
| #351 | Relocate top-level clutter | ✅ Moved |

### Active Beta Gate (H2)

| Issue | Title | Status |
|---|---|---|
| #182 | LB-04: Run and document a live rollback drill | 🟡 In Progress — Synology NAS at 192.168.1.10 available |

---

## 📋 Today's Target Issues

- [x] **Issue #346:** MODEL_POLICY.md describes a Copilot ladder that no longer matches the OpenCode setup — *Acceptance Criteria:* MODEL_POLICY.md updated to reflect current OpenCode tool routing; Copilot references removed or updated; file passes markdownlint
- [x] **Issue #350:** Consolidate the two opencode workflow files — *Acceptance Criteria:* Single `.github/workflows/opencode.yml` file; duplicate triggers removed; `opencode.yaml` deleted; workflow validates with `actionlint`
- [x] **Issue #352:** Required merge gate depends on a beta-tagged reusable workflow — *Acceptance Criteria:* Merge gate references stable workflow version (not beta tag); PR #362's main-ci-guard check updated

---

## ⚡ Execution Protocol

### 1. Test-Driven Development (`superpower:test-driven-development`)

#### Issue #346 — MODEL_POLICY.md

- [ ] **RED:** Write a test that validates MODEL_POLICY.md does not contain "Copilot" references that mislead agents
- [ ] **GREEN:** Update MODEL_POLICY.md to reflect current OpenCode setup
- [ ] **REFACTOR:** Clean up formatting, ensure consistency with other docs

#### Issue #350 — Consolidate opencode workflows

- [ ] **RED:** Verify both workflows currently exist and have overlapping triggers
- [ ] **GREEN:** Merge into single `opencode.yml`, remove `opencode.yaml`
- [ ] **REFACTOR:** Validate with `actionlint`, ensure no broken references

#### Issue #352 — Merge gate beta dependency

- [ ] **RED:** Check current main-ci-guard.yml for beta-tagged references
- [ ] **GREEN:** Update to stable workflow version
- [ ] **REFACTOR:** Verify all required status checks still pass

### 2. Verification & Code Review (`request-code-review`)

- [ ] Run `pre-commit run --all-files` — all hooks pass
- [ ] Run `make test-unit` — unit tests pass
- [ ] Run `npx markdownlint-cli` on modified .md files — no errors
- [ ] Review `git diff` against existing repository patterns
- [ ] Trigger `request-code-review` before committing

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
| #346 MODEL_POLICY.md | P1 Documentation Reconciliation | H2 Late Beta | Discovery Before Build |
| #350 opencode workflows | P1 Documentation Reconciliation | H2 Late Beta | GitOps Reconciliation |
| #352 merge gate | P1 Active Beta Gates | H2 Late Beta | GitOps Reconciliation |

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
