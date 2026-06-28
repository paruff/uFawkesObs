# Specification — OBS-AI-02: Prometheus AI Recording Rules and Alerts

**Source:** GitHub Issue #56 — OBS-AI-02
**Priority:** P1 (Sprint 3)
**Labels:** `sprint-3`, `ai-observability`
**Dependency:** OBS-AI-01 must be merged first (AI metrics pipeline in OTel Collector)

---

## Problem Statement

Once the AI metrics pipeline exists (OBS-AI-01), we need recording rules to compute derived metrics from `gen_ai.*` signals and alert thresholds based on DORA 2025 AI capability model thresholds. The critical metric is **rework rate** — DORA 2025's north star for AI health. Threshold: >20% = stop features, fix AI instructions.

---

## Requirements

### Functional Requirements

1. **FR-1:** New rule file `config/prometheus/ai-rules.yml` created
2. **FR-2:** Recording rules defined for:
   - `ai:llm_request_latency_p99:seconds` — p99 LLM response time from histogram data
   - `ai:llm_request_latency_p50:seconds` — p50 LLM response time from histogram data
   - `ai:token_usage_rate:per_minute` — LLM tokens consumed per minute
   - `ai:suggestion_acceptance_rate:ratio` — accepted / total suggestions (guarded with `or vector(0)`)
3. **FR-3:** Alert rules defined:
   - `AILLMLatencyHigh` — p99 > 10s for 5 minutes, severity: warning
   - `AIReworkRateHigh` — rework rate > 10% for 7 days, severity: warning (watch threshold)
   - `AIReworkRateCritical` — rework rate > 20% for 7 days, severity: critical (stop-features threshold)
   - `AITokenBudgetHigh` — token usage rate > configurable threshold, severity: warning
4. **FR-4:** `AIReworkRateCritical` annotation includes DORA 2025 reference
5. **FR-5:** All alerts have `category: ai-capability` label
6. **FR-6:** `config/prometheus/prometheus.yaml` `rule_files:` includes `ai-rules.yml`
7. **FR-7:** Stub `docs/ai-runbook.md` created with sections for each AI alert

### Non-functional Requirements

8. **NFR-1:** `promtool check rules` passes on `config/prometheus/ai-rules.yml`
9. **NFR-2:** `yamllint` passes on all new YAML files
10. **NFR-3:** All recording rules with arithmetic use `or vector(0)` guard per promql skill
11. **NFR-4:** All alert rules have corresponding `absent()` guards per promql skill
12. **NFR-5:** `docs/CHANGE_IMPACT_MAP.md` updated with ai-rules.yml entry

---

## Acceptance Criteria

- [ ] `config/prometheus/ai-rules.yml` exists with recording rules for latency P99, P50, token rate, acceptance rate
- [ ] Alert rules exist for `AILLMLatencyHigh`, `AIReworkRateHigh`, `AIReworkRateCritical`, `AITokenBudgetHigh`
- [ ] All alerts have `category: ai-capability` label
- [ ] `AIReworkRateCritical` has DORA 2025 annotation
- [ ] `config/prometheus/prometheus.yaml` `rule_files:` includes `ai-rules.yml`
- [ ] `promtool check rules config/prometheus/ai-rules.yml` passes
- [ ] `yamllint config/prometheus/ai-rules.yml` passes
- [ ] `docs/ai-runbook.md` exists with sections for each alert
- [ ] `docs/CHANGE_IMPACT_MAP.md` has ai-rules.yml entry
- [ ] All existing unit tests still pass

---

## Out of Scope

- AI capability dashboard (OBS-AI-03, issue #57)
- AI observability documentation (OBS-AI-04, issue #58)
- Changes to OTel Collector config
- DORA recording rules (requires M4-01 human gate)
