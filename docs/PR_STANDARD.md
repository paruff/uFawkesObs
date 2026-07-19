# PR Standards — uFawkesObs

## Title Format

PR titles follow **Conventional Commits**:

```
type(scope): description
```

| Type     | When to Use                                                |
| -------- | ---------------------------------------------------------- |
| `feat`   | New feature, service, or dashboard                         |
| `fix`    | Bug fix, configuration correction                          |
| `docs`   | Documentation-only changes                                 |
| `chore`  | Maintenance, dependency updates, tooling                   |
| `refactor` | Code/configuration restructuring with no behavior change |
| `test`   | Adding or fixing tests                                     |
| `ci`     | CI/CD pipeline or workflow changes                         |

**Rules:**
- Scope is optional but recommended: `fix(prometheus):`, `feat(grafana):`
- First word after `:` must be **lowercase**
- No trailing period
- Max 72 characters for the title line

**Examples:**
- `feat(grafana): add DORA metrics dashboard`
- `fix(prometheus): correct scrape interval for otel-collector`
- `chore(deps): bump tempo to 2.10.5`
- `docs: add alloy migration guide`

## Branch Naming

Branches must follow the same type prefix convention:

```
feat/<short-slug>
fix/<short-slug>
chore/<short-slug>
docs/<short-slug>
```

**Examples:**
- `feat/dora-dashboard`
- `fix/prometheus-scrape-interval`
- `chore/deps-tempo-2.10.5`

## PR Body

Every PR must include the **AI-Assisted Review Block** (see `AGENTS.md §7`):

```markdown
## AI-Assisted Review Block

**What does this PR do?**
[1-3 sentence summary]

**What could go wrong?**
[Honest assessment of risk — config changes, service restarts, data loss]

**What tests cover this change?**
[List specific tests or "Manual — no automated test exists for this path"]

**Architecture check:**
- What layer(s) were touched and are they correct per AGENTS.md §4?
- Any cross-plane impact (uFawkesPipe, uFawkesRes, uFawkesDORA)?

**What I was NOT sure about:**
[Anything uncertain — reviewers should focus here]
```

## CI Requirements

Before a PR can merge:

- [ ] All CI checks pass (pre-commit, unit tests, acceptance smoke, config validation)
- [ ] `main-ci-guard` passes (CI on main is green)
- [ ] PR size is under 400 lines (or has `large-pr-approved` label)
- [ ] Review has been approved
- [ ] Verification has passed

## Image Version Bumps

PRs that change image versions in `compose.yaml` must include:
- Old version
- New version
- Change reason (e.g., "CVE-2024-xxx fixed in new version")

## Prometheus Scrape Config Changes

PRs that change Prometheus scrape config must include:
- Which metrics will be affected
- Any new or removed scrape targets
- Impact on existing dashboards and alerts
