# ADR-008: Standardise Telemetry-Pipeline Config on OTel Collector YAML

**Status:** Proposed
**Date:** 2026-10-15
**Companion issue:** #503
**Scope:** Which configuration paradigm new telemetry-pipeline work uses, and what
happens to the existing Alloy River config.

---

## Context

Two pipeline configs coexist today:

| Component | File | Paradigm | Does |
|-----------|------|----------|------|
| `otel-collector` (contrib 0.162.0) | `config/otel/collector.yaml`, `collector-dora.yaml` | Collector YAML | OTLP ingest, `memory_limiter`/`batch`, `filter/ai` + `attributes/ai` (gen_ai.*), export to Prometheus, Tempo, Loki |
| `alloy` (v1.14.2) | `config/alloy/config.river` (80 lines) | River DSL | Docker container discovery and relabel, log scrape to Loki, embedded cAdvisor scrape to Prometheus remote-write |

Two languages mean two validation paths, two sets of docs, and two places to look
when a signal goes missing. Every OTLP signal, which is where the AI-observability
work lives (`otel-semantic-conventions`), already runs through the Collector.
Alloy's remaining job is host-level log and container-metric collection.

## Decision

**OTel Collector YAML is the single pipeline paradigm.** All new receivers,
processors, exporters and pipeline wiring are written as Collector YAML.

- No new River configuration. `config/alloy/config.river` is frozen: bug fixes only.
- Alloy keeps running until its two jobs have Collector equivalents
  (`filelog`/Docker log collection to Loki, `docker_stats` or an equivalent
  cAdvisor replacement to Prometheus). Removing it is a separate, later change.

## Rationale

- Collector YAML is the vendor-neutral, CNCF-standard format; the Fawkes
  Kubernetes track consumes the same Collector config unchanged.
- The pipeline that matters most (OTLP and gen_ai.*) is already Collector-only.
- Alloy's River adds a proprietary DSL for ~80 lines of config; consolidating
  removes a validation test, a doc and an image.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Standardise on Alloy River | Would mean porting 586 lines of Collector YAML to a Grafana-specific DSL for no capability gain; Alloy can embed Collector components but with lagging version parity. |
| Keep both indefinitely | The status quo this ADR exists to end. |

## Consequences for existing configs

- `config/otel/*.yaml`: unchanged; remain the source of truth.
- `config/alloy/config.river`, `docs/alloy-operations.md`,
  `tests/unit/test_alloy_config_validation.py`, the `alloy` compose service: kept
  as-is, marked transitional. Changes to them need a note in the PR.
- Follow-up (needs its own issue, PM sign-off per `.claude/rules/compose.md`):
  port log and container-metric collection to the Collector, then remove the
  `alloy` service, River file, doc and tests. Watch for label parity
  (`container`, `compose_service`, `compose_project`) since dashboards and
  Loki queries depend on them (see `docs/CHANGE_IMPACT_MAP.md`).
- Risk: `docker_stats` does not match cAdvisor metric names, so dashboards
  using `container_*` series need a compatibility check before cutover.
