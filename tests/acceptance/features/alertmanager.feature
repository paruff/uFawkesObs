@smoke
Feature: Alertmanager Integration (OBS-ACCEPTANCE-003)
  Validates that Alertmanager is healthy, Prometheus can reach it,
  and alert rules are loaded correctly.

  Background:
    Given the core observability stack is running

  Scenario: Alertmanager is healthy
    When I check the Alertmanager health endpoint
    Then it should return HTTP 200
    And the configuration should be loaded successfully

  Scenario: Prometheus has alert rules loaded
    When I query Prometheus for alert rules
    Then at least 1 alerting rule should be present
    And the rules should have a "ufawkesobs_self_monitoring" group
