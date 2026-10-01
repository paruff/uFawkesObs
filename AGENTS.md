# AGENTS.md — uFawkesObs

This file is a short index. The detailed repo rules live in the path-scoped rule files and skills below; keep the detail there instead of duplicating it here.

## 1. Repo identity

- Repo: `paruff/uFawkesObs`
- Purpose: Compose-based uFawkes observability stack (OpenTelemetry, Prometheus, Tempo, Loki, Grafana, Alloy) with GitOps deployment over SSH.
- See: `README.md`, `docs/ARCHITECTURE.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/CHANGE_IMPACT_MAP.md`, `docs/MODEL_POLICY.md`.

## 2. Read before editing

- `compose.yaml` and related config files
- The relevant path rule: `.claude/rules/compose.md`, `.claude/rules/config.md`, `.claude/rules/scripts.md`, `.claude/rules/tests.md`, `.claude/rules/dashboards.md`
- The relevant operating skill: `.agents/skills/gitops-reconcile/SKILL.md`, `.agents/skills/pr-review-block/SKILL.md`, or any other skill for the area you are changing

## 3. Canonical enforcement

The detailed enforcement lives in the rule files and skills, not in this index:

- `.claude/rules/compose.md` — pinned image tags, healthchecks, explicit networks, named volumes, PM sign-off gate
- `.claude/rules/config.md` — declarative config, no secrets, Prometheus/Grafana/Alloy conventions
- `.claude/rules/scripts.md` — shell safety and shellcheck rules
- `.claude/rules/tests.md` — no deleting failing tests, no silent exception swallowing
- `.claude/rules/dashboards.md` — UID/tag/schemaVersion conventions
- `.agents/skills/gitops-reconcile/SKILL.md` — deployment, branch protection, rollback, and main-branch workflow
- `.agents/skills/pr-review-block/SKILL.md` — required PR review block

## 4. Hard rules

- Never commit secrets, `.env` files, or tokens.
- Never use `latest` image tags.
- Never delete failing tests to green a build.
- Never push directly to `main`; use feature branches and human merge.
- Use TDD order for changes: add failing test, implement, refactor.
- Ask before changing public interfaces, CI config, exposed ports, image versions, service layout, volume mounts, or new env vars.
- Treat `config/**`, `compose.yaml`, `.env.example`, and `dashboards/**` changes as production-facing.

## 5. PR and review flow

- Open PRs with the required AI-assisted review block from `.agents/skills/pr-review-block/SKILL.md`.
- If the change touches deploy or branch-protection logic, load the GitOps skill before editing.
- Review policy and required checks live in `REVIEW.md` and the relevant workflow files.

## 6. Suite and cross-plane impact

- This repo is the Compose-tier uFawkes observability plane.
- Check `docs/CHANGE_IMPACT_MAP.md` and `docs/KNOWN_LIMITATIONS.md` before changing shared config, deployments, or cross-plane integrations.
- The model policy is in `docs/MODEL_POLICY.md`; keep policy details there rather than duplicating them here.
