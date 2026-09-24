---
name: gitops-reconcile
description: "GitOps reconciliation and deploy-pipeline mechanics for uFawkesObs — how a push to main becomes a live change on the deploy host, required CI checks, and the rollback path. Use when touching deploy.yml, main-ci-guard.yml, or debugging why a merge to main didn't reconcile."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesAI
---

# Skill: GitOps Reconcile

> **Load trigger:** touching `deploy.yml`, `main-ci-guard.yml`, branch protection,
> or debugging a deploy/reconciliation failure.
> **Token cost:** Low

## Purpose

uFawkesObs is trunk-based with push-triggered GitOps reconciliation over SSH
(ADR-003) — not a controller loop, not pull-based. This skill is the mechanics
an agent needs when working on that pipeline; `AGENTS.md` §8 states the rules,
this skill explains how they're actually implemented.

## Branch & PR Discipline

- Development happens on feature branches off `main`; never commit directly to trunk.
- Branch naming: `feat/<short-slug>` for features, `fix/<short-slug>` for fixes.
- CI runs on push and on PR. Local test-execution and CI are separate events —
  if CI fails after local tests passed, that's a repair-flow situation, not a
  sign the local run was wrong.
- PR size > 400 changed lines → CI blocks. Override requires a human-applied
  `large-pr-approved` label — agents never apply it themselves.
- Merge to trunk requires: green CI, review APPROVED, verification PASS,
  cross-validation PASS, and human approval.
- Image version bumps require old and new version in the PR description.
- Rework rate > 10% (PRs requiring a repair loop or more than one review
  cycle): stop adding features, fix instructions or gates instead.

## GitOps Reconciliation — What Actually Happens

Pushes to `main` for `config/**`, `compose.yaml`, `.env.example`, and
`dashboards/**` reconcile the target host over SSH:

1. Config-only changes use service reloads (Prometheus `/-/reload`, Alloy `SIGHUP`).
2. `compose.yaml` changes require GitHub Environment approval
   (`compose-restart`) before `make up` runs on the host.
3. The deploy target has no GNU Make — `deploy.yml`'s remote script inlines
   `make up`'s two underlying commands (`./scripts/check-env.sh` +
   `docker compose --profile core up -d`) directly instead of depending on it.

**deploy.yml only has a `workflow_run` trigger** — it fires automatically
after `Acceptance Full (Post-Merge)` completes on `main`. There is no
`workflow_dispatch`; merging the triggering PR is the way to re-run it, not
`gh workflow run`.

## Deployment Lifecycle Gates

**Main CI must be green before any PR merges.** What actually blocks a merge
is GitHub branch protection's required-status-checks list on `main`:
`Pre-commit Hooks`, `Security`, `Validate Configs`, `Unit Tests`,
`Integration Tests`, `Acceptance Smoke Tests`,
`🛡️ Main CI Health / 🛡️ Main CI Health`,
`🛡️ Acceptance Full Health / 🛡️ Main CI Health`.

`Acceptance Smoke Tests` is the job's own name inside `ci-acceptance-smoke.yml`
(not the workflow's display name, "Acceptance Smoke"). The last two checks
look identical after the slash because `main-ci-guard.yml`'s two jobs both
call the same reusable workflow
(`paruff/ufawkespipe/.github/workflows/reusable-main-ci-guard.yml@v1.3.0-beta.1`),
whose own internal job is always named `🛡️ Main CI Health` regardless of
caller — GitHub renders the check name as
`{caller job name} / {reusable job name}`, so only the prefix distinguishes
them. The two calls look at the most recent run of `Pre-Merge Pipeline` and
`Acceptance Full (Post-Merge)` on `main` respectively and fail the PR if
either was not `success` — this is what closes the gap where `main` could
look "green" while Acceptance Full was actually failing.

**Every push to `main` that changes config, compose, or dashboards triggers a
deploy**, and the deploy must include:

1. The deploy operation itself (SSH pull + reload/restart).
2. **Post-deployment verification** — smoke tests against the live deployed
   instance (health endpoints, data flow checks), not just against the CI
   build. Runs as a separate job after the deploy.
3. **Rollback on failure** — if post-deployment verification fails, the
   deploy must automatically revert the GitOps repo (`git revert`) and
   optionally restart the previous stack.

**Observability is built-in.** Every CI job logs `job-start` / `job-finish`
timestamps. Build times, test results, deploy status, and rollback events are
all traceable in uFawkesObs.

**Progressive delivery is aspirational.** The current model is SSH push with
`make up`. A staged model (canary → staging → production) should be designed
before uFawkesObs serves production traffic — see `docs/DEPLOYMENT_STRATEGY.md`.

## Known Failure Modes (real incidents)

- **Stale `DEPLOY_PATH` repo variable**: `vars.DEPLOY_PATH` can silently hold a
  dead path indefinitely (found holding a macOS dev path months after the
  deploy target changed). If deploy fails with `Repository not found at ...`,
  check this variable before anything else: `gh variable list --repo paruff/uFawkesObs`.
- **Missing `.env` on a fresh clone**: the deploy host's `.env` isn't
  git-tracked. A fresh checkout has no `GRAFANA_ADMIN_PASSWORD`, causing
  `check-env.sh` to fail with "missing or insecure". Fix: `cp .env.example
  .env` on the host and set a real password before the next deploy attempt.
- **Docker context pointing at itself**: if the deploy host has a custom
  `docker context` (e.g. one created for remote management) set as *current*,
  every `docker` command on that host — including the ones the deploy script
  runs — can route through a broken self-referential SSH loop. Check
  `docker context ls` on the host if `docker compose` commands there fail with
  SSH errors; `docker context use default` fixes it.

## See Also

- `AGENTS.md` §8 — the rules this skill implements
- `docs/PATH_TO_LATE_BETA.md`, `docs/PREPARE_FOR_PUBLIC_RELEASE.md`, ADR-003
- Reusable workflows: `paruff/ufawkespipe`'s `reusable-main-ci-guard.yml@v1.3.0-beta.1`, `reusable-rollback.yml@v1.2.0`
