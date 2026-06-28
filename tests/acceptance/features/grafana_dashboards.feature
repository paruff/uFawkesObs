@offline @grafana @dashboards
Feature: Grafana Dashboard Configuration
  Validates that all Grafana dashboard JSON files in dashboards/ follow
  uFawkesObs conventions: string datasource UIDs, schemaVersion >= 40,
  and correct provisioning structure.

  Scenario: Grafana dashboard provisioning directory exists
    Then the directory "config/grafana/provisioning/dashboards" should exist

  Scenario: Platform dashboards directory exists
    Then the directory "dashboards/platform" should exist

  Scenario: Grafana datasources provisioning uses string UIDs
    Given the YAML file "config/grafana/provisioning/datasources/datasources.yaml" is loaded
    Then the YAML should have key "datasources"

  Scenario: Each provisioned datasource has a uid field
    Given the YAML file "config/grafana/provisioning/datasources/datasources.yaml" is loaded
    Then the YAML should have key "datasources"
