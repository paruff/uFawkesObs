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
- **Suite membership:** uFawkesAI

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

If any of these don't exist for this repo, agents proceed with what's
available and note the gap — they don't invent the missing content.

## 4. Architecture Rules — Never Violate These

### compose.yaml

- All service image versions must be **pinned** — no `latest` tags ever
- Secrets and passwords go in `.env` (gitignored) — never in `compose.yaml`
- All services must have `healthcheck:` defined
- Networks must be explicitly declared — no implicit default network
- Volumes for persistent data must be named, not anonymous
- Profiles (`core`, `dora`) must be explicit and validated with `docker compose --profile <name> config`

### config/ files

- Config files are **declarative** — no scripts or logic inside them
- OpenTelemetry collector config: exporters must match actual running services
- Prometheus scrape targets must match actual service names in `compose.yaml`
- Grafana datasources must reference services by Docker Compose service name, not `localhost`
- No credentials in config files — use environment variable substitution (`${VAR_NAME}`)
- Alloy River DSL config: use `config.alloy` naming convention

### scripts/

- `set -euo pipefail` at the top of every `.sh` file
- `shellcheck` must pass on all scripts
- No hardcoded container names — read from `compose.yaml` or environment variables
- Health check scripts must exit non-zero on failure

### tests/

- Unit tests in `tests/unit/` — validate config YAML, JSON, and conventions
- Integration tests in `tests/integration/` — BDD-style, run against running stack
- Acceptance tests in `tests/acceptance/` — verify the stack is observable
- Every test must have a clear pass/fail exit code
- Never delete failing tests to make a build pass

### dashboards/

- Grafana dashboard JSON files in `dashboards/platform/` and `dashboards/services/`
- All datasource UIDs must be string references (e.g. `prometheus`, `tempo`, `loki`, `ufawkesres-postgres`) — never numeric IDs
- schemaVersion must be 39 (Grafana 12.x)
- UID convention: `ufawkesobs-<slug>`
- Tags must include `ufawkesobs` for platform dashboards

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
- Remove `healthcheck:` from any service **except**:
  - The image is **distroless** (no shell, no curl, no wget, no python), **AND**
  - The image binary itself provides no health-query subcommand (`validate`, `status`, etc.).
  - When removing, document in the PR description: the image name, why it's distroless, and the alternative approach used (`condition: service_started`, metrics endpoint, etc.).
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
headings, update `review.md`'s check to match.

```markdown
## AI-Assisted Review Block

**What does this PR do?**
[...]

**What could go wrong?**
[...]

**What tests cover this change?**
[...]

**Architecture check:**
- What layer(s) were touched and are they correct per §4?
- Any cross-plane impact (uFawkesPipe, uFawkesRes, uFawkesDORA)?

**What I was NOT sure about:**
[...]
```

## 8. GitOps / Trunk-Based Delivery Contract

### Branch & PR Discipline
- Development happens on feature branches off `main`; never commit directly to trunk.
- Branch naming: `feat/<short-slug>` for features, `fix/<short-slug>` for fixes.
- CI runs on push and on PR. `feature-flow`'s local test-execution and CI are separate events — if CI fails after local tests passed, `repair-flow` handles it.
- PR size > 400 changed lines → CI blocks. Override requires a human-applied `large-pr-approved` label — agents never apply it themselves.
- Merge to trunk requires: green CI, review APPROVED, verification PASS, cross-validation PASS, and human approval.
- Image version bumps require old and new version in PR description.
- Any change to Prometheus scrape config requires a note on which metrics will be affected.
- Rework rate > 10% (PRs requiring `repair-flow` or more than one review cycle): stop adding features, fix instructions or gates.

### GitOps Reconciliation
- GitOps reconciliation: pushes to `main` for `config/**`, `compose.yaml`, `.env.example`, and `dashboards/**` reconcile the target host over SSH.
- Config-only changes use service reloads (Prometheus `/-/reload`, Alloy `SIGHUP`).
- `compose.yaml` changes require GitHub Environment approval (`compose-restart`) before `make up`.

### Deployment Lifecycle Gates
- **Main CI must be green before any PR merges.** If the latest run of `CI Pipeline` (or `ci.yml`) on `main` is not `success`, all PRs are blocked until it is fixed. This is enforced by a `main-ci-guard.yml` workflow — see prei's implementation for reference.
- **Every push to `main` that changes config, compose, or dashboards triggers a deploy.** The deploy must include:
  1. The deploy operation itself (SSH pull + reload/restart).
  2. **Post-deployment verification** — smoke tests against the live deployed instance (health endpoints, data flow checks), not just against the CI build. This runs as a separate job after the deploy.
  3. **Rollback on failure** — if post-deployment verification fails, the deploy must automatically revert the GitOps repo (`git revert`) and optionally restart the previous stack.
- **Observability is built-in.** Every CI job logs `job-start` / `job-finish` timestamps. Build times, test results, deploy status, and rollback events are all traceable in uFawkesObs.
- **Progressive delivery is aspirational.** The current model is SSH push with `make up`. A staged model (canary → staging → production) should be designed before uFawkesObs serves production traffic. See `docs/DEPLOYMENT_STRATEGY.md` (proposed) for the target.

## 9. Known Limitations

See `docs/KNOWN_LIMITATIONS.md` — known issues across storage, networking, profiles, and cross-plane integration. Do not make these worse.

## 10. Suite Integration

uFawkesObs is part of the **uFawkesAI** suite and the **Fawkes IDP** ecosystem.

**Depends on:**
- **uFawkesRes** — Shared PostgreSQL for DORA metric snapshots (`datasources.yaml` UID: `ufawkesres-postgres`)
- **uFawkesDORA** — DORA compute engine consuming OTel spans via `otel-collector-dora` profile

**Depended on by:**
- **uFawkesPipe** — Pipeline lifecycle telemetry flows into uFawkesObs Tempo
- **uFawkesDevX** — Developer environment metrics flow into uFawkesObs
- **fawkes** — Full IDP deployment uses uFawkesObs as its observability layer

When making changes, check `docs/CHANGE_IMPACT_MAP.md` for cross-plane impact.

## 11. See Also

- `.github/copilot-instructions.md` — Copilot-specific subset
- `.github/instructions/` — path-scoped instruction files
- `docs/PROMPT_LIBRARY.md` — tested prompt templates
- `docs/CHANGE_IMPACT_MAP.md` — cross-service and cross-plane impact
- `docs/MODEL_POLICY.md` — model selection, routing, and budget guardrails
