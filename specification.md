# Specification — OBS-AI-03: Grafana AI Capabilities Dashboard

**Source:** GitHub Issue #57 — OBS-AI-03
**Priority:** P1 (Sprint 3)
**Labels:** `sprint-3`, `ai-observability`
**Dependency:** OBS-AI-02 must be merged first (Prometheus AI recording rules)

---

## Problem Statement

OBS-AI-01 (OTel `metrics/ai` pipeline) and OBS-AI-02 (Prometheus AI recording/alerts rules)
provide the data collection and aggregation layers. Without a dashboard, operators cannot
visualise AI model performance, token consumption, suggestion acceptance trends, or
rework rate — the DORA 2025 north star metric for AI health.

---

## Requirements

### Functional Requirements

1. **FR-1:** New dashboard `dashboards/platform/ai-capabilities.json` created
2. **FR-2:** Dashboard includes stat panels for:
   - LLM p99 latency (current value with DORA thresholds)
   - Token usage rate (current value)
   - Suggestion acceptance rate (current % with thresholds)
   - AI rework rate (current % with DORA 2025 thresholds)
3. **FR-3:** Dashboard includes time-series panels for:
   - LLM latency P99/P50 over time
   - Token usage rate over time
   - Suggestion acceptance rate trend
   - AI rework rate trend
4. **FR-4:** AI active alert list panel showing firing AI-capability alerts
5. **FR-5:** DORA 2025 performance band thresholds applied to latency and rework rate panels
6. **FR-6:** Datasource UIDs use string references (`prometheus`), not numeric IDs

### Non-functional Requirements

7. **NFR-1:** Dashboard JSON is valid JSON
8. **NFR-2:** `schemaVersion` set to 40 (Grafana 12.x)
9. **NFR-3:** All panel queries use the `prometheus` datasource UID
10. **NFR-4:** Dashboard auto-loads via provisioning (placed in `dashboards/platform/`)

---

## Acceptance Criteria

- [ ] `dashboards/platform/ai-capabilities.json` exists with valid JSON
- [ ] Stat panels for: P99 latency, token rate, acceptance rate, rework rate
- [ ] Time-series panels for: latency P99/P50, token rate, acceptance trend, rework trend
- [ ] AI alert list panel shows AI-capability alerts
- [ ] DORA 2025 thresholds applied (latency: <1s Elite, <5s High, <10s Medium, >=10s Low)
- [ ] All datasource references use UID `prometheus`
- [ ] `schemaVersion` is 40
- [ ] `python3 -m json.tool` validates JSON syntax
- [ ] No numeric datasource IDs in the file

---

## Out of Scope

- AI observability documentation (OBS-AI-04, issue #58)
- DORA metrics dashboard (M4-04, issue #83)
- Changes to OTel Collector config or Prometheus rules
- DORA recording rules (requires M4-01 human gate)
