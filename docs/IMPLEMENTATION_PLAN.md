# Implementation Plan — uFawkesObs

> Generated from platform audit (June 2026). Integrates existing GitHub issues (#64, #71, #74-87) with 16 new findings from codebase review. Updated as issues are completed.

---

## Audit-to-Issue Mapping

### Existing Issues

| Issue | Title | Milestone | Phase |
|---|---|---|---|
| #64 | Add LICENSE file (Apache 2.0) | M0 | 2 |
| #71 | Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates | M2 | 3 |
| #74 | Publish and verify docs/ | M2 | 3 |
| #75 | Add GitHub repository metadata and CI badge | M2 | 3 |
| #76 | uFawkesPipe → uFawkesObs integration guide | M3 | 4 |
| #77 | uFawkesDevX → uFawkesObs integration guide | M3 | 4 |
| #78 | Register in fawkes Backstage catalog | M3 | 4 |
| #79 | Update multi-stack-integration.md | M3 | 4 |
| #80 | Define DORA data contract spec | M4 | 5 |
| #81 | Add DevLake to compose stack | M4 | 5 |
| #82 | Add DORA recording rules | M4 | 5 |
| #83 | Provision DORA metrics dashboard | M4 | 5 |
| #84 | Document K8s deployment strategy (ADR) | M5 | 6 |
| #85 | Create Helm chart | M5 | 6 |
| #86 | k3d quick-start and Makefile targets | M5 | 6 |
| #87 | K8s acceptance test CI workflow | M5 | 6 |
| #63 | Implement GitOps standards across all repos | — | 7 |

### New Issues from Audit

| ID | Finding | Severity | Proposed Issue | Phase |
|---|---|---|---|---|
| N1 | otel-collector missing `restart: unless-stopped` | CRITICAL | `fix(compose): add restart policy and resource limits to otel-collector` | 0 |
| N2 | otel-collector missing `deploy.resources` limits | CRITICAL | (combined with N1) | 0 |
| N3 | All 4 Grafana datasources missing `uid:` fields | CRITICAL | `fix(grafana): add explicit uid fields to all provisioned datasources` | 0 |
| N4 | Dashboard provisioning path mismatch — 16 new dashboards not loading | CRITICAL | `fix(grafana): fix dashboard provisioning path mismatch in new-dashboards.yaml` | 0 |
| N5 | All 9 runbook URLs in alerts.yml point to wrong repo | HIGH | `fix(prometheus): correct runbook URLs from Obstackd to uFawkesObs` | 1 |
| N6 | All 9 alerts in alerts.yml missing `absent()` guards | HIGH | `fix(prometheus): add absent() guards to all alerts.yml rules` | 1 |
| N7 | Test files hardcode `admin:admin` credentials | HIGH | `fix(tests): replace hardcoded admin:admin with $GRAFANA_ADMIN_PASSWORD` | 1 |
| N8 | Legacy dashboards use schemaVersion 38 (should be 39) | HIGH | `fix(grafana): upgrade legacy dashboards to schemaVersion 39` | 3 |
| N9 | Makefile only runs 1 of 4 acceptance tests | MEDIUM | `fix(make): wire all acceptance tests into make test-acceptance` | 1 |
| N10 | Loki `table_manager` deprecated | LOW | `fix(loki): remove deprecated table_manager section` | 3 |
| N11 | Alloy missing `depends_on: prometheus` | MEDIUM | `fix(compose): add depends_on prometheus to alloy service` | 1 |
| N12 | Service dashboard UIDs missing `ufawkesobs-` prefix | LOW | `fix(grafana): add ufawkesobs- prefix to service dashboard UIDs` | 3 |
| N13 | Stale migration files in repo root | LOW | `chore: move stale migration files to docs/history/` | 0 |
| N14 | `.bak` file committed in config/grafana/dashboards/ | LOW | `chore: remove .bak file from config/grafana/dashboards/` | 0 |
| N15 | `e2e-runner.sh` uses `chmod -R 777` | LOW | `fix(scripts): replace chmod 777 with proper permission handling` | 3 |
| N16 | OTel `debug` exporter at `verbosity: detailed` | LOW | `chore(otel): reduce debug exporter verbosity to normal` | 3 |

---

## Phase 0 — Critical Fixes (unblocks everything else)

Must be fixed first. The dashboard provisioning path mismatch means 16 dashboards are invisible. The missing datasource UIDs mean dashboards will break on any Grafana restart. The otel-collector gaps mean no crash recovery and unbounded resource usage.

| Order | ID | Title | Effort | Model | Files | Status |
|---|---|---|---|---|---|---|
| 0.1 | N1+N2 | Add restart policy and resource limits to otel-collector | XS | GPT-5 mini | `compose.yaml` | ⬜ |
| 0.2 | N3 | Add explicit uid fields to all provisioned datasources | XS | GPT-5 mini | `config/grafana/provisioning/datasources/datasources.yaml` | ⬜ |
| 0.3 | N4 | Fix dashboard provisioning path mismatch | S | GPT-4.1 | `config/grafana/provisioning/dashboards/new-dashboards.yaml`, `compose.yaml` | ⬜ |
| 0.4 | N13+N14 | Clean stale files from repo root and config/ | XS | GPT-5 mini | `ALLOY_IMPLEMENTATION.md`, `ALLOY_SUMMARY.txt`, `MIGRATION_SUMMARY.md`, `config/grafana/dashboards/observability-stack-health.json.bak` | ⬜ |

**Dependency:** All 4 are independent — run in parallel.

**Verification:**
- `docker compose up -d && docker compose ps` — all healthy
- `curl http://localhost:3000/api/datasources | jq '.[].uid'` — all UIDs present
- `curl http://localhost:3000/api/search | jq '.[].uid'` — 16 new dashboards appear

**Decision (N4):** Option A chosen — fix `compose.yaml` to add volume mounts matching the provisioner intent (`dashboards/platform/` → `/etc/grafana/dashboards/platform`, `dashboards/services/` → `/etc/grafana/dashboards/services`). This keeps the clean folder separation.

---

## Phase 1 — Alerting & Testing Correctness

Fix correctness issues that don't block the stack from running but mean alerts won't fire when they should and tests don't match the security model.

| Order | ID | Title | Effort | Model | Files | Status |
|---|---|---|---|---|---|---|
| 1.1 | N5 | Correct runbook URLs from Obstackd to uFawkesObs | XS | GPT-5 mini | `config/prometheus/alerts.yml` | ⬜ |
| 1.2 | N6 | Add absent() guards to all alerts.yml rules | M | GPT-5.1-Codex | `config/prometheus/alerts.yml` | ⬜ |
| 1.3 | N7 | Replace hardcoded admin:admin with $GRAFANA_ADMIN_PASSWORD | S | GPT-4.1 | 4 test files in `tests/acceptance/` and `scripts/grafana/` | ⬜ |
| 1.4 | N9 | Wire all acceptance tests into make test-acceptance | XS | GPT-5 mini | `Makefile` | ⬜ |
| 1.5 | N11 | Add depends_on prometheus to alloy service | XS | GPT-5 mini | `compose.yaml` | ⬜ |

**Dependency:** All 5 are independent — run in parallel.

**Verification:**
- `promtool check rules config/prometheus/alerts.yml` — passes
- `grep -c "absent(" config/prometheus/alerts.yml` — returns ≥9
- `make test-acceptance` — runs all 4 tests

**Decision (N12):** Keep both `alerts.yml` and `ufawkesobs-self-monitoring.yml`. Add `absent()` guards to `alerts.yml`. Do not consolidate — they serve different purposes (service-specific vs platform-level).

---

## Phase 2 — M0 Completion

| Order | ID | Title | Effort | Model | Files | Status |
|---|---|---|---|---|---|---|
| 2.1 | #64 | Add LICENSE file (Apache 2.0) | XS | GPT-5 mini | `LICENSE`, `README.md` | ⬜ |

**Dependency:** None. Independent of Phase 0 and 1.

---

## Phase 3 — M2 Completion (Release Quality)

| Order | ID | Title | Effort | Model | Files | Blocked By | Status |
|---|---|---|---|---|---|---|---|
| 3.1 | #71 | Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates | M | GPT-5 mini | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `README.md` | — | ⬜ |
| 3.2 | #74 | Publish and verify docs/ | M | GPT-4.1 | `docs/ARCHITECTURE.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/CHANGE_IMPACT_MAP.md`, `docs/history/`, `README.md` | — | ⬜ |
| 3.3 | #75 | Add GitHub repository metadata and CI badge | XS | GPT-5 mini | `README.md` | — | ⬜ |
| 3.4 | N8 | Upgrade legacy dashboards to schemaVersion 39 | M | GPT-4.1 | `config/grafana/dashboards/*.json` | Phase 0.3 | ⬜ |
| 3.5 | N10 | Remove deprecated table_manager from Loki config | XS | GPT-5 mini | `config/loki/loki.yaml` | — | ⬜ |
| 3.6 | N12 | Add ufawkesobs- prefix to service dashboard UIDs | S | GPT-4.1 | `dashboards/services/*.json` | Phase 0.3 | ⬜ |
| 3.7 | N15 | Replace chmod 777 in e2e-runner.sh | XS | GPT-5 mini | `tests/acceptance/e2e-runner.sh` | — | ⬜ |
| 3.8 | N16 | Reduce OTel debug exporter verbosity | XS | GPT-5 mini | `config/otel/collector.yaml` | — | ⬜ |

**Dependency:** 3.4 and 3.6 depend on Phase 0.3 (dashboard provisioning fix). Rest are independent.

---

## Phase 4 — M3 Completion (Ecosystem Integration)

| Order | ID | Title | Effort | Model | Blocked By | Status |
|---|---|---|---|---|---|---|
| 4.1 | #76 | uFawkesPipe → uFawkesObs integration guide | M | GPT-4.1 | — | ⬜ |
| 4.2 | #77 | uFawkesDevX → uFawkesObs integration guide | M | GPT-4.1 | — | ⬜ |
| 4.3 | #78 | Register in fawkes Backstage catalog | S | GPT-5 mini | — | ⬜ |
| 4.4 | #79 | Update multi-stack-integration.md | S | GPT-5 mini | — | ⬜ |

**Dependency:** All independent. Can run in parallel.

---

## Phase 5 — M4 Completion (DORA Metrics)

Sequential — each depends on the previous. Human gate required between 5.1 and 5.2.

| Order | ID | Title | Effort | Model | Blocked By | Status |
|---|---|---|---|---|---|---|
| 5.1 | #80 | Define DORA data contract spec | L | GPT-5.1-Codex | — | ⬜ |
| 5.2 | #81 | Add DevLake to compose stack | XL | GPT-4.1 | 5.1 (spec-approved label) | ⬜ |
| 5.3 | #82 | Add DORA recording rules | L | GPT-5.1-Codex | 5.1, 5.2 | ⬜ |
| 5.4 | #83 | Provision DORA metrics dashboard | M | GPT-5.1-Codex | 5.3 | ⬜ |

**Dependency:** Strictly sequential. Human gate: maintainer must add `spec-approved` label to #80 before #81 is assigned.

---

## Phase 6 — M5 Completion (Kubernetes)

Sequential — each depends on the previous. Can run in parallel with Phases 3-5.

| Order | ID | Title | Effort | Model | Blocked By | Status |
|---|---|---|---|---|---|---|
| 6.1 | #84 | Document K8s deployment strategy (ADR) | M | GPT-5 mini | — | ⬜ |
| 6.2 | #85 | Create Helm chart | XL | GPT-5.1-Codex | 6.1 | ⬜ |
| 6.3 | #86 | k3d quick-start and Makefile targets | M | GPT-4.1 | 6.2 | ⬜ |
| 6.4 | #87 | K8s acceptance test CI workflow | M | GPT-4.1 | 6.3 | ⬜ |

---

## Phase 7 — GitOps Standards

| Order | ID | Title | Effort | Model | Blocked By | Status |
|---|---|---|---|---|---|---|
| 7.1 | #63 | Implement GitOps standards across all repos | L | GPT-4.1 | — | ⬜ |

**Dependency:** Independent. Can run anytime.

---

## Execution Timeline (Parallel Tracks)

```
Week 1:  Phase 0 (critical fixes) ──── all 4 parallel
         Phase 2 (#64 LICENSE) ──────── independent
Week 2:  Phase 1 (alerting/testing) ── all 5 parallel
         Phase 3.1-3.3 (M2 docs) ───── parallel with Phase 1
Week 3:  Phase 3.4-3.8 (dashboards) ─ depends on Phase 0.3
         Phase 4 (integration guides) ─ all 4 parallel
Week 4+: Phase 5 (DORA) ────────────── sequential, human gate
         Phase 6 (K8s) ──────────────── sequential, parallel with Phase 5
         Phase 7 (GitOps) ───────────── anytime
```

---

## Open Decisions

| ID | Decision | Default | Rationale |
|---|---|---|---|
| D1 | Dashboard provisioning path (N4) | Option A: fix compose.yaml mounts to match provisioner intent | Keeps clean folder separation between platform/ and services/ |
| D2 | alerts.yml consolidation (N6) | Keep both files, add absent() guards to alerts.yml | They serve different purposes (service-specific vs platform-level) |
| D3 | DORA phase timing (Phase 5) | Include in plan with human gate noted | Blocks downstream milestones; plan should show full picture |

---

## Progress Log

| Date | Event | Issues Completed |
|---|---|---|
| 2026-06-07 | Plan created from platform audit | — |
