@smoke @contract
Feature: Multi-Plane Telemetry Contract (OBS-CONTRACT-001-004)
  Validates that external consumers (uFawkesPipe, uFawkesDevX, generic apps)
  can send OTLP telemetry to uFawkesObs and see it queryable in the
  respective backends. These are the core cross-plane integration contracts.

  Background:
    Given the core observability stack is running

  @smoke @contract
  Scenario: OBS-CONTRACT-001 — External OTLP trace ingested by Tempo
    When an external plane sends a synthetic OTLP trace via gRPC
    Then the trace should be queryable via Tempo API within 15 seconds
    And the trace should have at least 3 spans preserved

  @smoke @contract
  Scenario: OBS-CONTRACT-002 — External OTLP metric scraped by Prometheus
    When an external plane sends a counter metric "acceptance_test_requests" with value 42
    Then the metric should appear in Prometheus within 30 seconds
    And the metric should have labels: "test_id", "service_name"

  @smoke @contract
  Scenario: OBS-CONTRACT-003 — External OTLP log indexed by Loki
    When an external plane sends a structured JSON log via OTLP logs signal
    Then the log should be queryable in Loki within 20 seconds
    And the log body should parse as valid JSON with the original keys preserved

  @smoke @contract
  Scenario: OBS-CONTRACT-004 — Cross-plane datasource resolution
    When an external plane queries Grafana API for datasources
    Then the Prometheus datasource should use "http://prometheus:9090"
    And the Tempo datasource should use "http://tempo:3200"
    And the Loki datasource should use "http://loki:3100"
    And the Alertmanager datasource should use "http://alertmanager:9093"
