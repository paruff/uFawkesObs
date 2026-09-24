# AGENTS.md — uFawkesObs

> Shared template across all repos this harness operates on. Copy to each
> repo's root and fill only the bracketed sections. Keep section numbers
> 4, 6, 7 as-is — `review.md`, `test.md`, and `feature-flow.md` reference
> them by number. Everything else may be trimmed to what this repo
> actually needs; a repo with no Kubernetes, for instance, can delete
> that line from §4 rather than leave it as dead weight.
>
> What's deliberately NOT here: model selection, token budgets, premium
> request accounting. That's repo-specific operating cost, not shared
> governance — keep it in a separate `docs/MODEL_POLICY.md` per repo if
> needed, so this file stays portable across repos with very different
> cost profiles (a docs-only repo and a high-volume PromQL repo shouldn't
> share a model ladder). **uFawkesObs model policy lives in `docs/MODEL_POLICY.md`.**

---

## 1. Identity

- **Repo:** paruff/uFawkesObs
- **What this is:** The observability plane of the Fawkes IDP family — OpenTelemetry, Prometheus, Tempo, Loki, Grafana, and Alloy delivered as Docker Compose with GitOps reconciliation over SSH.
- **Suite membership:** uFawkes (Compose tier) — active suite is Obs, Pipe, DevX, Dojo. This repo's `AGENTS.md`/agent conventions are scaffolded from the [uFawkesAI](https://github.com/paruff/uFawkesAI) template, which is tooling shared across the family, not a suite-tier peer.

## 2. Where the Agents Live

Agents and skills are shared, not repo-local: `~/.config/opencode/agents/`
and `~/.config/opencode/skills/`. This file does not redefine them — it
tells the shared agents how to behave *in this repo specifically*.

Standard pipeline, in order:

```
discover → spec → design → plan
                              │
                              ▼
                        feature-flow
        (branch → build → test-execution → review →
         verification → cross-validation → delivery-prep)
                              │
                              ▼
                    [push, PR, CI, human merge]
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
            repair-flow              release → measure → learn
         (if CI disagrees          (post-merge cadence,
          with local test)          closes the loop)
```

`discovery-flow` routes into the top half (discovery through planning).
`feature-flow` owns everything from a planned feature to an open PR.
It never merges — that is always human-gated. `repair-flow` is the
CI-failure-specific repair loop, separate from feature-flow's own local
test gate. `measure` and `learn` run on schedule or trigger, not as
steps another agent calls directly.

## 3. Context Files — Read Before Generating Anything

| Priority | File                         | What You Learn                                                     |
| -------- | ---------------------------- | ------------------------------------------------------------------ |
| 1        | `AGENTS.md` (this file)      | Identity, governance, GitOps contract                              |
| 2        | `compose.yaml`               | Service versions, ports, volumes, networks, profiles               |
| 2.5      | `docs/adr/README.md`         | Technology decisions — Loki version, Compose scope, GitOps scope   |
| 3        | `docs/ARCHITECTURE.md`       | How services connect and depend on each other                      |
| 4        | `docs/KNOWN_LIMITATIONS.md`  | Known issues — do not make these worse                             |
| 4.5      | `docs/MODEL_POLICY.md`       | Model selection, token budgets, premium request accounting         |
| 5        | `docs/CHANGE_IMPACT_MAP.md`  | What breaks when a service config changes                          |
| 5.5      | `docs/DEPLOYMENT_STRATEGY.md` | Progressive delivery model — must exist before production traffic  |
| 5.6      | `docs/PR_STANDARD.md`        | PR title and body format rules                                     |
| 5.7      | `docs/PATH_TO_LATE_BETA.md`  | Beta readiness bar and open gaps — do not close as "beta ready" until these clear |
| 5.8      | `docs/PREPARE_FOR_PUBLIC_RELEASE.md` | Public-release blockers (strangers, no maintainer present) — separate bar from late beta |
| 5.9      | `docs/DETERMINISM.md`        | Build/CI reproducibility gaps and roadmap (now/should/future) |
| 5.10     | `docs/TESTING_PYRAMID.md`    | Testcontainers + InSpec plan — catching more per run, not just reproducibility |
| 6        | `VISION.md`                  | North Star, core principles, explicit non-goals (years horizon)   |
| 6.1      | `MILESTONES.md`              | Horizons (H1/H2/H3), release gates, epic sequencing (months)     |
| 6.2      | `EXECUTION_QUEUE.md`         | Prioritized tasks ready for work (weeks)                          |
| 6.3      | `plan-for-the-day.md`        | Daily execution: single goal, TDD cycle, session learnings        |

### Planning Cascade

The four planning documents form a strictly nested cascade:

```
VISION.md (years) → MILESTONES.md (months) → EXECUTION_QUEUE.md (weeks) → plan-for-the-day.md (today)
```

- **Strict Top-Down Traceability:** Every task in `plan-for-the-day.md` originates from `EXECUTION_QUEUE.md`, which fulfills a delivery gate in `MILESTONES.md`, moving toward `VISION.md`.
- **Scope Drift Protection:** Before adding a feature to `EXECUTION_QUEUE.md`, check it against `VISION.md` non-goals.
- **Controlled Bottom-Up Feedback:** Learnings from `plan-for-the-day.md` route back to `EXECUTION_QUEUE.md` for reprioritization.

### Product Artifacts

| File | Purpose |
|---|---|
| `docs/product/discovery-draft.md` | JTBD, riskiest assumption, acceptance criterion |
| `docs/product/spec.md` | Functional requirements (OBS-F##, OBS-N##), interface contracts |
| `docs/product/design.md` | Architecture principles, repo structure, component topology |
| `docs/product/tasks.json` | Reserved for future product-level task output |

If any of these don't exist for this repo, agents proceed with what's
available and note the gap — they don't invent the missing content.

## 4. Architecture Rules — Never Violate These

Path-scoped in `.claude/rules/` so each set loads only when that path is
touched, instead of staying in every agent's context always:

| Path | Rules file |
|---|---|
| `compose.yaml` | `.claude/rules/compose.md` — pinned images, healthchecks, named volumes, explicit networks |
| `config/**` | `.claude/rules/config.md` — declarative only, no hardcoded credentials |
| `scripts/**` | `.claude/rules/scripts.md` — `set -euo pipefail`, shellcheck-clean |
| `tests/**` | `.claude/rules/tests.md` — never delete a failing test, never swallow an exception silently |
| `dashboards/**` | `.claude/rules/dashboards.md` — UID/tag/schemaVersion conventions |

Read the relevant file before editing that path. These are hard rules, not
suggestions — violating one blocks merge (§8).

## 5. The PM–Agent Contract

### Agents MAY Do Without Asking

- Read any file
- Edit code, tests, docs within the scope of an assigned task
- Run: `docker compose config` (validate), `yamllint`, `shellcheck`, pre-commit
- Open draft PRs

### Agents MUST Ask Before

- Adding or removing dependencies (requires PM sign-off)
- Changing public interfaces or API contracts
- Modifying CI/CD pipeline configuration
- Changing image versions in `compose.yaml`
- Adding or removing services from `compose.yaml`
- Changing exposed port numbers
- Modifying volume mount paths
- Adding new environment variables

### Agents Must NEVER

- Commit `.env` files, passwords, API keys, or tokens
- Use `latest` image tags
- Remove `healthcheck:` from any service without following the distroless
  exception documented in `.claude/rules/compose.md`
- Delete tests to make a build pass
- Push to `main` directly or merge their own PRs
- Apply `large-pr-approved` label (humans only)
- Mark a task complete when validation failed

## 6. TDD Commit Order

```
1. test: add failing tests for [feature]   ← CI fails here intentionally
2. feat: implement [feature] to pass tests
3. refactor: clean up [feature] if needed
```

Never combine a failing test commit with an implementation commit.

Commit message format: `feat(scope):`, `fix(scope):`, `test(scope):`,
`docs:`, `chore:` — reference issue number: `fix(prometheus): correct scrape interval (#8)`

## 7. AI-Assisted Review Block

Every PR opened by an agent must include this block in its description.
`review.md` checks for this literal structure — if you change the
headings, update `review.md`'s check to match. See skill: `pr-review-block`
for the exact template.

## 8. GitOps / Trunk-Based Delivery Contract

- Feature branches off `main` (`feat/<slug>`, `fix/<slug>`); never commit to trunk directly.
- PR size > 400 changed lines → CI blocks (override: human-applied `large-pr-approved` label only).
- Merge requires: green CI, review APPROVED, verification PASS, cross-validation PASS, human approval.
- A push to `main` touching `config/**`, `compose.yaml`, `.env.example`, or
  `dashboards/**` triggers a real SSH deploy to the target host — treat every
  such change as production-facing.
- Rework rate > 10% (PRs needing a repair loop or 2+ review cycles): stop
  adding features, fix instructions or gates instead.

Full mechanics — required branch-protection checks, why two checks share a
name, the deploy/rollback pipeline, known failure modes — are in the
`gitops-reconcile` skill (`.agents/skills/gitops-reconcile/SKILL.md`). Load it
before touching `deploy.yml`, `main-ci-guard.yml`, or debugging a
reconciliation failure.

## 9. Known Limitations

See `docs/KNOWN_LIMITATIONS.md` — known issues across storage, networking, profiles, and cross-plane integration. Do not make these worse.

## 10. Suite Integration

uFawkesObs is the Compose-tier of the **uFawkes** suite (Obs, Pipe, DevX,
Dojo) within the **Fawkes IDP** ecosystem — see `README.md` § Part of the
Fawkes IDP.

- **Depends on:** nothing. DORA's datastore is SQLite only, permanently — the
  uFawkesRes Postgres integration was fully removed (retired 2026-08-18, see
  `docs/notes/res-status.md`); a resource plane belongs in Fawkes (Kubernetes
  track) instead, see `docs/fawkes-migration.md`. uFawkesDORA (archived) was
  merged into this repo's `dora/` directory.
- **Depended on by:** uFawkesPipe (telemetry → Tempo), uFawkesDevX (metrics).
  **fawkes does NOT depend on uFawkesObs** — it runs its own Kubernetes-native
  stack and replaces uFawkesObs wholesale on graduation; see `docs/fawkes-migration.md`.

Check `docs/CHANGE_IMPACT_MAP.md` for cross-plane impact before changing shared config.

## 11. See Also

- `INTENT.md` — half-page anchor, read this first
- `.claude/rules/` — path-scoped architecture rules (§4)
- `.agents/skills/gitops-reconcile/` — deploy/reconciliation mechanics (§8)
- `.github/copilot-instructions.md` — Copilot-specific subset
- `.github/instructions/` — path-scoped instruction files
- `docs/PROMPT_LIBRARY.md` — tested prompt templates
- `docs/CHANGE_IMPACT_MAP.md` — cross-service and cross-plane impact
- `docs/MODEL_POLICY.md` — model selection, routing, and budget guardrails
- `docs/DEPLOYMENT_STRATEGY.md` — progressive delivery plan
- `docs/PREPARE_FOR_PUBLIC_RELEASE.md` — public-release blockers, separate from late-beta readiness
- `docs/PR_STANDARD.md` — PR title and body format rules
- `docs/RELEASE_PROCESS.md` — automated release cadence (release-please, issue #264)
- `paruff/ufawkespipe` reusable workflows — `reusable-main-ci-guard.yml`, `reusable-rollback.yml` (`@v1.2.0`)
