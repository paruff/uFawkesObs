# Design — M2-02: GitOps Standards

**Based on:** specification.md (M2-02), Keep a Changelog format, Dependabot docs

---

## Impacted Components

| Component | File | Change Type |
|---|---|---|
| Dependabot config | `.github/dependabot.yml` | **Update** — add Docker ecosystem |
| Funding config | `.github/FUNDING.yml` | **Update** — fix array syntax |
| Changelog | `CHANGELOG.md` | **Create** — Keep a Changelog v1.1.0 |
| Git tag | `v0.1.0` | **Apply** — semver tag on main |
| GitHub label | `good-first-issue` | **Create** — repo label |

---

## Technical Approach

### 1. `.github/dependabot.yml` Update

Current config has only `github-actions` ecosystem. Add Docker ecosystem with weekly
schedule and explicit version pinning strategy:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

Docker ecosystem scans `compose.yaml` and any `Dockerfile` for base image updates.

### 2. `.github/FUNDING.yml` Fix

Current: `github: paruff` (string — ignored by GitHub)
Target: `github: [paruff]` (array — renders funding button)

GitHub FUNDING.yml requires array format for multiple funders. Single funder still
requires `[` brackets `]`.

### 3. `CHANGELOG.md` Creation

Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) v1.1.0 format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ...

## [0.1.0] — 2026-06-28

### Added
- Initial OpenTelemetry-based observability stack
- ...
```

Include entries for all merged work up to this point (Loki 3.3.2 migration, Grafana 12
upgrade, OTel AI pipeline, Prometheus AI rules, Grafana AI dashboard, AI observability docs).

### 4. CODEOWNERS

Already exists with `* @paruff` — no change needed.

### 5. Tag `v0.1.0`

`git tag v0.1.0 && git push origin v0.1.0`

Applied from `main` at the current HEAD.

### 6. `good-first-issue` Label

`gh label create good-first-issue --description "Good for new contributors" --color "7057ff"`

Then apply to 3–5 open issues that are well-scoped and documented.

---

## Constraints

1. Dependabot Docker ecosystem scans from `compose.yaml` — no additional config needed
2. Tags must be signed or annotated per repo conventions (annotated: `git tag -a`)
3. CHANGELOG.md must be valid markdown (markdownlint)
4. Label creation requires `gh` CLI with repo write access
