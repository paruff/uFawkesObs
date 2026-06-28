# Specification — M2-02: GitOps Standards

**Source:** GitHub Issue #63
**Priority:** P0
**Labels:** `repo-standards`

---

## Problem Statement

uFawkesObs lacks standard repository metadata and automation. Dependabot is not configured
for Docker image updates, FUNDING.yml uses incorrect syntax, CHANGELOG.md does not exist,
and no semantic version tag has been applied. These gaps make the repository harder to
maintain and less discoverable.

---

## Requirements

### Functional Requirements

1. **FR-1:** `.github/dependabot.yml` configured with both Docker and GitHub Actions ecosystems,
   weekly update schedule
2. **FR-2:** `.github/FUNDING.yml` exists with `github: [paruff]` (array format)
3. **FR-3:** `CHANGELOG.md` at repo root in Keep a Changelog format with initial v0.1.0 entry
4. **FR-4:** `.github/CODEOWNERS` exists with `* @paruff`
5. **FR-5:** Git tag `v0.1.0` applied to current main
6. **FR-6:** `good-first-issue` label created and applied to 3–5 open issues

### Non-functional Requirements

7. **NFR-1:** All YAML files pass `yamllint`
8. **NFR-2:** `CHANGELOG.md` passes `markdownlint`
9. **NFR-3:** Tag follows semver convention (`vMAJOR.MINOR.PATCH`)

---

## Acceptance Criteria

- [ ] `.github/dependabot.yml` includes Docker and GitHub Actions ecosystems
- [ ] `.github/FUNDING.yml` uses `github: [paruff]` array format
- [ ] `CHANGELOG.md` exists with v0.1.0 initial release entry
- [ ] `.github/CODEOWNERS` exists with `* @paruff`
- [ ] Tag `v0.1.0` applied to main
- [ ] `good-first-issue` label exists on GitHub
- [ ] 3–5 issues have `good-first-issue` label applied

---

## Out of Scope

- CONTRIBUTING.md and CODE_OF_CONDUCT.md (M2-01, issue #71)
- Issue templates (M2-01)
- Repository description and topics (M2-04, issue #75)
- CI badge in README (M2-04)
