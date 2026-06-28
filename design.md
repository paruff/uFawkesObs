# Design — OBS-AI-04: AI Observability Documentation

**Based on:** specification.md (OBS-AI-04), existing doc patterns

---

## Impacted Components

| Component | File | Change Type |
|---|---|---|
| AI observability guide | `docs/ai-observability-guide.md` | **Create** — full reference doc |
| Agent instructions | `AGENTS.md` | Update version table + AI refs |
| OTel collector skill | `.agents/skills/otel-collector/SKILL.md` | Update AI pipeline section |
| Change impact map | `docs/CHANGE_IMPACT_MAP.md` | Add AI entries |

---

## Technical Approach

### 1. `docs/ai-observability-guide.md`

Structure following existing runbook/doc conventions:

```
# AI Observability Guide

## Overview
Brief: what OBS-AI-01/02/03 provide together.

## Architecture
ASCII diagram showing: App → OTel metrics/ai pipeline → Prometheus rules → Grafana dashboard

## Metrics Reference
Table of all gen_ai.* raw metrics and ai:* recording rules with descriptions and PromQL.

## Alert Reference
Table of all AI alert rules with thresholds, severity, and DORA band.

## Grafana Dashboard
How to find and interpret the AI capabilities dashboard.
Screenshot description and panel-by-panel guide.

## Instrumenting Your Application
How to emit gen_ai.* telemetry from Python/Node/Go services.
OTel SDK configuration, required attributes, exporter endpoint.

## DORA 2025 Thresholds
Reference table for Elite/High/Medium/Low bands.
```

### 2. `AGENTS.md` Updates

- Fix version table: Alertmanager v0.27.0 → v0.28.0, Loki v2.9.10 → v3.3.2, Grafana v10.4.5 → v12.3.7
- Add `docs/ai-observability-guide.md` to Context Files table (priority 4.5)
- Add AI observability references in appropriate sections

### 3. `.agents/skills/otel-collector/SKILL.md` Updates

- Fix AI pipeline section to match actual `config/otel/collector.yaml`:
  - Add `filter/ai` and `attributes/ai` processors
  - Add `metrics/ai` pipeline with correct processor ordering
  - Update exporter references (uses `prometheus` not `prometheusremotewrite`)
  - Remove stale `prometheusremotewrite/ai` reference

### 4. `docs/CHANGE_IMPACT_MAP.md` Updates

- Add rows for `config/otel/collector.yaml` AI processor changes
- Add rows for `dashboards/platform/ai-capabilities.json`

---

## Constraints

1. All documentation must follow existing Markdown conventions (markdownlint)
2. AGENTS.md version table must match `compose.yaml` exactly
3. Do not modify `compose.yaml`, Prometheus config, OTel config, or dashboard JSON
4. Do not modify existing sections of AGENTS.md that are unrelated to AI or versions
