# plan-for-the-day.md — uFawkesObs

> **Horizon:** Today | **Owner:** Active contributor | **Review:** End of session
> **Feeds into:** [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) ← source

---

## Today's Goal

*Pull 1–3 items from [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) for focused daily execution.*

---

## Session Log

<!-- Fill this in at the start of each session -->

**Date:** YYYY-MM-DD
**Contributor:** (name or agent)
**Starting from:** EXECUTION_QUEUE.md P0/P1 items

---

## Tasks for Today

| # | Task | Source | Status | TDD Cycle |
|---|---|---|---|---|
| 1 | | | ⬜ Not started | RED → GREEN → REFACTOR |
| 2 | | | ⬜ Not started | RED → GREEN → REFACTOR |
| 3 | | | ⬜ Not started | RED → GREEN → REFACTOR |

---

## TDD Cycle Log

For each task, record:

### Task 1: [title]

**RED — Write failing test:**
```bash
# Command run and output
```
- [ ] Test fails for expected reason

**GREEN — Minimal implementation:**
```bash
# Command run and output
```
- [ ] Test passes
- [ ] Other tests still pass

**REFACTOR — Clean up:**
```bash
# Command run and output
```
- [ ] Tests still pass
- [ ] No new warnings

---

## Session Learnings

Capture anything discovered during today's work that should feed back into [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md):

- **Tech debt discovered:** (new issues to file)
- **Assumptions invalidated:** (what we thought was true but isn't)
- **Scope drift detected:** (work that crept beyond the task boundary)
- **Blockers hit:** (what stopped progress)

---

## End-of-Day Checklist

- [ ] All tasks marked complete or explicitly deferred
- [ ] Tests pass locally (`make test-unit`, `make test-acceptance-smoke`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Changes committed with conventional commit messages
- [ ] Learnings captured above
- [ ] New tasks (if any) added to EXECUTION_QUEUE.md

---

## Traceability

Every task in this file must originate from [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md), which fulfills a specific delivery gate in [`MILESTONES.md`](MILESTONES.md), moving the project toward [`VISION.md`](VISION.md).

```
VISION.md (years) → MILESTONES.md (months) → EXECUTION_QUEUE.md (weeks) → plan-for-the-day.md (today)
```

**Scope Drift Protection:** Before adding work not in the queue, check it against VISION.md non-goals. If it violates core principles, reject it.

**Bottom-Up Feedback:** Learnings above route back to EXECUTION_QUEUE.md for reprioritization — they bypass MILESTONES.md and VISION.md.

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`VISION.md`](VISION.md) | Years | Why does this product exist? What are the non-goals? |
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| **plan-for-the-day.md** (this file) | Today | What am I doing right now? |
