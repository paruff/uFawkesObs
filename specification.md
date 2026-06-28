# Specification — OBS-AI-04: AI Observability Documentation

**Source:** GitHub Issue #58 — OBS-AI-04
**Priority:** P1 (Sprint 3)
**Labels:** `sprint-3`, `ai-observability`
**Dependency:** OBS-AI-02, OBS-AI-03 must be merged first

---

## Problem Statement

OBS-AI-01 (OTel `metrics/ai` pipeline), OBS-AI-02 (Prometheus AI recording rules), and
OBS-AI-03 (Grafana AI dashboard) are complete. Operators and agent contributors need
documentation to understand how AI observability works in uFawkesObs, how to emit
`gen_ai.*` telemetry, how to interpret the AI capabilities dashboard, and how to
respond to AI alerts. AGENTS.md also needs updating to reflect the AI pipeline and
to fix stale version references.

---

## Requirements

### Functional Requirements

1. **FR-1:** `docs/ai-observability-guide.md` created covering:
   - Architecture: OTel AI pipeline → Prometheus rules → Grafana dashboard
   - Metrics reference: available `gen_ai.*` and `ai:*` metrics
   - Alert reference: all AI alert rules with thresholds
   - Dashboard guide: how to view AI capabilities in Grafana
   - Instrumentation guide: how apps emit AI telemetry
   - DORA 2025 AI thresholds: latency, acceptance rate, rework rate bands
2. **FR-2:** `AGENTS.md` updated with:
   - Correct service versions (Loki 3.3.2, Grafana 12.3.7, Alertmanager 0.28.0)
   - AI pipeline architecture reference
   - New context file entry for `docs/ai-observability-guide.md`
3. **FR-3:** `.agents/skills/otel-collector/SKILL.md` updated to match actual AI pipeline config
4. **FR-4:** `docs/CHANGE_IMPACT_MAP.md` updated with AI-related entries

### Non-functional Requirements

5. **NFR-1:** All markdown files pass markdownlint
6. **NFR-2:** All existing unit tests continue to pass

---

## Acceptance Criteria

- [ ] `docs/ai-observability-guide.md` exists with full AI observability reference
- [ ] `AGENTS.md` version table matches `compose.yaml`
- [ ] `AGENTS.md` references AI observability guide in context files
- [ ] `.agents/skills/otel-collector/SKILL.md` AI pipeline section matches actual config
- [ ] `docs/CHANGE_IMPACT_MAP.md` has AI-related entries
- [ ] markdownlint passes
- [ ] All 239+ unit tests pass

---

## Out of Scope

- Grafana dashboard changes (OBS-AI-03)
- Prometheus rule changes (OBS-AI-02)
- OTel Collector config changes (OBS-AI-01)
- Changes to `compose.yaml`
