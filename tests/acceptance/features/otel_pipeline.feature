@smoke
Feature: OTel Pipeline Health (OBS-ACCEPTANCE-001)
  Validates that the OpenTelemetry Collector and Prometheus are operating
  correctly and that OTel metrics are queryable end-to-end.

  Background:
    Given the core observability stack is running

  Scenario: OTel Collector is healthy with self-metrics
    When I check the OTel Collector metrics endpoint
    Then the endpoint should return HTTP 200
    And the response should contain "otelcol_process_uptime"

  Scenario: Prometheus scrapes the OTel Collector target
    When I query Prometheus for 'up{job="otel-collector"}'
    Then the result should have value "1"
    And the scrape duration should be under 1 second

  Scenario: OTel metrics are visible in Grafana
    Given the "Prometheus" datasource is configured in Grafana
    When I query Grafana for "otelcol_process_uptime" via the Prometheus datasource
    Then the response should contain at least 1 data point
    And the data point value should be positive
