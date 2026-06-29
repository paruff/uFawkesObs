@full
Feature: SLI/SLO Test Gates (OBS-SLI-001-006)
  Measures and gates on telemetry system quality — not just availability.
  Each scenario captures latency measurements and compares them against
  defined SLO targets. All scenarios are @full (post-merge) because
  latency measurement requires sampling windows too slow for pre-merge.

  Background:
    Given the core observability stack is running

  @full
  Scenario: OBS-SLI-001 — OTLP to Prometheus scrape latency (SLO: p99 < 30s)
    When I emit a counter metric "slo_ingest_latency" with a unique value
    Then the metric should appear in Prometheus within 60 seconds
    And the ingestion latency should be less than 30 seconds

  @full
  Scenario: OBS-SLI-002 — Log ingestion latency (SLO: p99 < 15s)
    When I emit a structured JSON log via OTLP
    Then the log should appear in Loki within 30 seconds
    And the log ingestion latency should be less than 15 seconds

  @full
  Scenario: OBS-SLI-003 — Trace ingestion latency (SLO: p99 < 20s)
    When I emit a synthetic trace with 3 spans via OTLP
    Then the trace should appear in Tempo within 30 seconds
    And the trace ingestion latency should be less than 20 seconds

  @full
  Scenario: OBS-SLI-004 — Scrape completeness (SLO: 100% targets UP)
    When I query Prometheus for the "up" metric
    Then all core scrape targets should report UP (value=1)

  @full
  Scenario: OBS-SLI-005 — Grafana datasource health (SLO: 100% reachable)
    When I query the Grafana API for datasource health
    Then all configured datasources should be reachable

  @full
  Scenario: OBS-SLI-006 — Dashboard data freshness (SLO: all dashboards show data within 5m)
    When I query each provisioned Grafana dashboard for panel data
    Then at least one panel per dashboard should return non-empty results
