# Design — M2-04: Add Repository Metadata, Topics, and CI Badge

**Based on:** specification.md (M2-04)

---

## Impacted Components

| Component | File / Resource | Change Type |
|---|---|---|
| README test count | `README.md` | **Update** — 118 → 239 |
| GitHub repo metadata | GitHub API | **Update** — homepage URL + topics |

---

## Technical Approach

### 1. CI Badge (Already Present)

Line 3 of README.md:
```markdown
[![CI](https://github.com/paruff/uFawkesObs/actions/workflows/ci.yml/badge.svg)](https://github.com/paruff/uFawkesObs/actions/workflows/ci.yml)
```

Verified present — no change needed.

### 2. Update Test Count

Line 404 in README.md:
```
**Test coverage:** 118 tests covering all configuration aspects
```
→ Change to `239` (count from `pytest tests/unit/`).

### 3. Set Homepage URL

`gh repo edit --homepage "https://ufawkes.dev"` — sets the project landing page URL
on the GitHub repo sidebar.

### 4. Add Missing Topics

Current topics: devops, dora-metrics, grafana, observability, open-source,
platform-engineering, prometheus, ufawkes

Missing: opentelemetry, docker-compose, gitops, alertmanager, tempo, loki

`gh repo edit --add-topic opentelemetry,docker-compose,gitops,alertmanager,tempo,loki`

---

## Constraints

1. Homepage URL must be a valid URL
2. GitHub topics are limited to printable ASCII characters
3. README.md must pass markdownlint after edits
