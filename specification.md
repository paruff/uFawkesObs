# Specification — OBS-AI-01: Add AI Metrics Pipeline to OTel Collector Config

**Source:** GitHub Issue #55 — OBS-AI-01
**Priority:** P1 (Sprint 3)
**Labels:** `sprint-3`, `ai-observability`

---

## Problem Statement

DORA 2025 identifies AI adoption as a key capability but warns it increases instability without control systems. To track AI capability maturity, uFawkesObs needs to collect AI-specific signals: LLM latency, token usage, acceptance rates, and rework rate. The OTel Collector is already running and is the correct ingestion point — it just needs an AI-specific pipeline added.

This follows the OpenLLMetry semantic conventions (`gen_ai.*` attribute namespace) which are now part of the OTel specification.

---

## Requirements

### Functional Requirements

1. **FR-1:** `config/otel/collector.yaml` must contain a new pipeline `metrics/ai`
2. **FR-2:** The `metrics/ai` pipeline uses the existing `otlp` receiver (AI SDKs send via OTLP — no new receiver needed)
3. **FR-3:** A new `filter/ai` processor must be added that passes through metrics matching `gen_ai\..*`, `llm\..*`, `openllmetry\..*`, or `ai\..*`
4. **FR-4:** A new `attributes/ai` processor must be added that inserts `ai.environment=development` and `ai.platform=fawkes-idp` on all AI metrics
5. **FR-5:** The `metrics/ai` pipeline exports to the existing `prometheus` exporter (port 8889)
6. **FR-6:** The `service.pipelines.metrics/ai` must be wired: `receivers: [otlp]`, `processors: [memory_limiter, filter/ai, attributes/ai, batch]`, `exporters: [prometheus]`

### Non-functional Requirements

7. **NFR-1:** Existing `metrics`, `traces`, `logs` pipelines must NOT be modified
8. **NFR-2:** `yamllint` must pass on `config/otel/collector.yaml`
9. **NFR-3:** The `filter/ai` processor uses `error_mode: ignore` so that if no AI metrics arrive (e.g. before AI tooling is integrated), the pipeline doesn't error
10. **NFR-4:** Unit test must be added verifying the `metrics/ai` pipeline exists in the config

---

## Acceptance Criteria

- [ ] `config/otel/collector.yaml` contains `metrics/ai` pipeline in `service.pipelines`
- [ ] `filter/ai` processor defined with `error_mode: ignore` and regexp include matching `gen_ai\..*`, `llm\..*`, `openllmetry\..*`, `ai\..*`
- [ ] `attributes/ai` processor defined with `ai.environment=development` and `ai.platform=fawkes-idp` insert actions
- [ ] `metrics/ai` pipeline wired: `receivers: [otlp]`, `processors: [memory_limiter, filter/ai, attributes/ai, batch]`, `exporters: [prometheus]`
- [ ] Existing `metrics`, `traces`, `logs` pipelines unchanged
- [ ] `yamllint` passes on `config/otel/collector.yaml`
- [ ] Unit test in `tests/unit/test_otel_config_validation.py` verifies `metrics/ai` pipeline exists
- [ ] All existing unit tests still pass

---

## Out of Scope

- Prometheus AI recording rules (OBS-AI-02, issue #56)
- Grafana AI capabilities dashboard (OBS-AI-03, issue #57)
- AI observability documentation (OBS-AI-04, issue #58)
- DORA recording rules (requires human gate on M4-01)
- Changes to `compose.yaml` (no service changes needed)
