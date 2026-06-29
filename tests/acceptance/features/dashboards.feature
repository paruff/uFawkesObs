@smoke
Feature: Grafana Dashboard Provisioning (OBS-ACCEPTANCE-004)
  Validates that Grafana dashboards are provisioned correctly and
  that expected datasources are configured.

  Background:
    Given the core observability stack is running

  Scenario: Grafana datasources are provisioned
    When I fetch the Grafana datasource list
    Then the list should contain a "Prometheus" datasource
    And the list should contain a "Loki" datasource
    And the list should contain a "Tempo" datasource
    And the list should contain a "Alertmanager" datasource

  Scenario: Core dashboards are provisioned
    When I fetch the Grafana dashboard list
    Then the list should contain a dashboard with UID "observability-stack-health"
    And the list should contain a dashboard with UID "application-performance"
    And the list should contain a dashboard with UID "platform-ufawkesobs-health"
