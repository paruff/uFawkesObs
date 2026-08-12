# Implementation Plan — uFawkesObs

> **Audit-derived remediation plan.** Last synced against repo state: 2026-07-27.
>
> This file previously redirected to `.agents/memory/plan.md`. That was wrong —
> `.agents/memory/plan.md` was last touched 2026-06-11 and uses a Phase/N-numbering
> scheme that no longer matches real GitHub issues. The actively maintained
> feature/milestone roadmap is **[`docs/plan.md`](plan.md)** (v1.1.0, updated
> 2026-07-01, tracked against real `gh issue list` numbers and merged PRs). Go there
> for "what feature work is next." This file is scoped to **repo hygiene and
> consistency findings** from the audit below — one-time cleanup, not ongoing
> feature milestones.

---

## Audit Summary

Overall repo health is good: `compose.yaml` follows AGENTS.md §4 (pinned versions,
healthchecks with documented distroless exceptions, explicit network, validated
profiles), main CI is green, ADRs are current, and governance docs
(`ARCHITECTURE.md`, `KNOWN_LIMITATIONS.md`, `CHANGE_IMPACT_MAP.md`,
`DEPLOYMENT_STRATEGY.md`, `MODEL_POLICY.md`, `PR_STANDARD.md`) are all present and
consistent with `compose.yaml`. The issues found are documentation/tracking drift
and repo-root hygiene, not architectural or runtime problems.

---

## Findings & Remediation Plan

### P0 — Broken or misleading pointers

**A1. This file pointed at the wrong plan.** Fixed by this edit — now points to
`docs/plan.md`. `.agents/memory/plan.md` should be deleted or explicitly marked
`ARCHIVED` at its top so agents reading it don't treat it as current.

**A2. `docs/plan.md` status column has drifted from GitHub issue state.**

- M2-01 (issue #71, CONTRIBUTING.md/CODE_OF_CONDUCT.md) shows `🔲 PENDING`, but
  `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` already exist at repo root. Issue #71
  is also still open on GitHub. The work is done; the tracking isn't.
- OBS-AI-02 (issue #56) and OBS-AI-03 (issue #57) show `🔲 PENDING` in
  `docs/plan.md` but are **CLOSED** on GitHub.

  Fix: reconcile `docs/plan.md`'s status column against `gh issue list --state
  all`, update statuses, close #71 if the acceptance criteria are actually met.

**A3. Issues #51, #52, #53, #54 (OBS-DORA-01/03/04/05) look superseded.** They
describe a DevLake + MySQL design that `docs/reviews/M4-02-ecosystem-review.md`
explicitly replaced (DevLake moved to uFawkesDORA, MySQL replaced by uFawkesRes
Postgres) — that replacement is what M4-02 (issue #81/#51, done, PR #148) actually
shipped. Fix: close #51–#54 as superseded by M4-01–M4-04, linking the ecosystem
review.

### P1 — Duplicate, diverging root docs (RESOLVED 2026-07-27)

**B1/B2.** Root `design.md`/`specification.md`/`tasks.json` turned out to be the
**Phase 5 (chaos/failure-injection) feature's** working docs, not a stale
duplicate of the product-level `docs/design.md`/`docs/specification.md` — the
content diff confirmed they describe different things entirely. Fix applied:
introduced two directories instead of a merge-and-delete:

- **`docs/product/`** — product-level, whole-repo docs: `spec.md` (was
  `docs/specification.md`), `design.md` (was `docs/design.md`),
  `discovery-draft.md` and `tasks.json` (new stubs — no product-level
  discovery doc or standalone task backlog existed before; `tasks.json` notes
  that `docs/plan.md` remains the actual milestone/task tracker so this
  doesn't duplicate it).
- **`docs/features/<feature-slug>/`** — per-feature pipeline output, kept
  after a feature ships. The chaos/failure-injection feature's root files
  moved to `docs/features/chaos-failure-injection/`. See
  `docs/features/README.md` for the convention.

Cross-references in `docs/multi-stack-integration.md` and
`docs/adr/ADR-006-dora-metric-definitions.md` updated to the new
`docs/product/spec.md` path. Root `design.md`/`specification.md`/`tasks.json`
stay `.gitignore`d (now root-anchored, `/design.md` etc., so they don't also
hide the `docs/product/` and `docs/features/` copies) as transient
feature-flow working files.

### P2 — Stray/untracked files at repo root

**C1.** `AGENTS.md.bak`, `ci-diagnosis.md`, `ci-fix-report.md`, `.unlighthouse/`,
and `.agents/logs/2026-07-19.jsonl` are untracked (`git status`). `ci-diagnosis.md`
and `ci-fix-report.md` read like generated agent-session output — the repo already
has `reports/` (with a `chaos-evidence/` subdirectory) for exactly this. Fix: move
anything with lasting value into `reports/`, delete the rest, and `.gitignore`
`.unlighthouse/` if it's a regenerable tool-output directory. `AGENTS.md.bak`
looks like a stray editor backup — confirm it's not in-progress work before
deleting.

**C2.** `build-report.md`, `test-report.md`, and `tasks.json` are tracked at repo
root and also look generated. Fix: relocate into `reports/` or add to
`.gitignore` and stop committing them, per the pattern the repo already
established for `reports/chaos-evidence/`.

### P2 — `compose.yaml`

**D1.** The `otel-collector-dora` service's `DORA_POSTGRES_URL` default embeds a
literal fallback password directly in `compose.yaml`:
`postgresql://ufawkesres:password@fawkes-postgres:5432/ufawkesres` <!-- pragma: allowlist secret -->.
AGENTS.md §4
says secrets belong only in `.env`. This is the same class of risk as the already
-documented `GRAFANA_ADMIN_PASSWORD:-admin` default in
`docs/KNOWN_LIMITATIONS.md`, but the Postgres default isn't documented there yet.
Fix: either remove the fallback so the `dora` profile fails closed without an
explicit `.env` value, or (if a local-dev default is genuinely wanted) add it to
`KNOWN_LIMITATIONS.md` alongside the Grafana admin-password entry so it's a
tracked, intentional risk rather than a silent one.

### P3 — Minor drift

**E1.** `CHANGELOG.md`'s `[Unreleased]` section only lists 2 small items
(the M2-02 label and dependabot Docker ecosystem) despite M3, M4, and the OBS-AI
milestone's worth of merged work landing since `[0.1.0]`. Fix: backfill
`[Unreleased]` (or cut a `0.2.0` entry) summarizing the M3/M4/OBS-AI-complete work,
then keep it current per merged PR going forward.

**F1.** `docs/OBSERVABILITY_STATUS.md` still references a "media-refinery" app
in its Loki query examples and log-source tables. The actual demo app in this repo
is `apps/telemetry-generator`. Fix: replace the `media-refinery` references with
`telemetry-generator` (compose service name, per `docs/ARCHITECTURE.md`).

---

## Execution Order

1. **A1** — done (2026-07-27).
2. **A2** — done (2026-07-27): statuses reconciled, issue #71 closed.
   **A3** — done (2026-08-12): #51–#54 closed as superseded (LB-07 #185),
   linking `docs/reviews/M4-02-ecosystem-review.md`. M4 tracking issues
   #80–#83 closed as superseded in the same pass.
3. **B1, B2** — done (2026-07-27): `docs/product/` and `docs/features/`
   introduced, see above.
4. **C1, C2** — root cleanup.
5. **D1** — compose.yaml secret default.
6. **E1, F1** — changelog backfill and stale app-name reference.

None of these block current feature work tracked in `docs/plan.md` (next up there:
M4-04 DORA dashboard, then Milestone 5 Kubernetes/Helm track). They're independent
hygiene fixes and can be picked up opportunistically or batched into one
`chore:` PR per AGENTS.md §6 commit conventions.
