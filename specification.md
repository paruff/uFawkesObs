# Specification — M2-04: Add Repository Metadata, Topics, and CI Badge

**Source:** GitHub Issue #75
**Priority:** P0
**Labels:** `documentation`, `chore`

---

## Problem Statement

The uFawkesObs repository landing page has gaps: the README test count is stale (118
vs actual 239), the GitHub homepage URL is not set, and repository topics are missing
key technology identifiers like `opentelemetry` and `docker-compose`. These gaps reduce
discoverability on GitHub and mislead visitors.

---

## Requirements

### Functional Requirements

1. **FR-1:** `README.md` includes a live CI badge for the main branch
2. **FR-2:** `README.md` test coverage count reflects actual test count (239, not 118)
3. **FR-3:** GitHub repository homepage URL is set to project URL
4. **FR-4:** GitHub repository topics include: `opentelemetry`, `docker-compose`, `gitops`,
   `alertmanager`, `tempo`, `loki`

### Non-functional Requirements

5. **NFR-1:** README.md passes markdownlint
6. **NFR-2:** Only README.md is modified (no compose.yaml, configs, etc.)

---

## Acceptance Criteria

- [ ] `README.md` has CI badge (verify present)
- [ ] `README.md` test count shows 239, not 118
- [ ] GitHub homepage URL is set
- [ ] GitHub topics include opentelemetry, docker-compose, gitops, alertmanager, tempo, loki

---

## Out of Scope

- Adding new README sections or restructuring content
- Changing compose.yaml or service configs
- Adding CONTRIBUTING.md or issue templates (M2-01)
