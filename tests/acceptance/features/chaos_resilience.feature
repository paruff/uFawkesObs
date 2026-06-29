@chaos
Feature: Chaos Resilience (OBS-CHAOS-001-005)
  Validates system behavior under failure — not just idle-healthy.
  Requires synthetic workload (Phase 4) running continuously to measure impact.

  Background:
    Given the core observability stack is running
    And synthetic telemetry is being generated

  @chaos
  Scenario: OBS-CHAOS-001 — Log pipeline survives Loki restart
    When I stop the "loki" service
    Then Alloy should continue running and buffering logs
    When I start the "loki" service after 30 seconds
    Then all buffered logs should be queryable in Loki within 120 seconds
    And the log count after restart should match the count before restart (+/- 5%)

  @chaos
  Scenario: OBS-CHAOS-002 — Metrics pipeline survives Prometheus restart
    When I stop the "prometheus" service
    Then existing metrics should still be queryable via Grafana (cached)
    When I start the "prometheus" service after 30 seconds
    Then Prometheus should resume scraping all targets within 60 seconds
    And metric gaps should not exceed 90 seconds

  @chaos
  Scenario: OBS-CHAOS-003 — OTel Collector restart is transparent
    Given synthetic telemetry is being generated
    When I restart the "otel-collector" service
    Then the trace pipeline should resume within 30 seconds
    And new traces should be queryable in Tempo within 30 seconds of restart

  @chaos
  Scenario: OBS-CHAOS-004 — Network partition self-heals
    When I disconnect the "otel-collector" from the observability network
    Then the OTel Collector should log connection errors (not crash)
    When I reconnect the "otel-collector" to the observability network after 20 seconds
    Then all telemetry pipelines should resume within 30 seconds

  @chaos
  Scenario: OBS-CHAOS-005 — Grafana datasource removal fails gracefully
    Given the Grafana datasources are provisioned
    When I remove a Grafana datasource provisioning file
    Then Grafana should continue serving cached dashboards
    And new queries should fail gracefully with appropriate error
