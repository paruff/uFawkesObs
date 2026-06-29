@smoke
Feature: Loki Log Pipeline (OBS-ACCEPTANCE-002)
  Validates that Loki is ingesting logs from Alloy and that logs
  are queryable via LogQL.

  Background:
    Given the core observability stack is running

  Scenario: Loki is ready and accepting queries
    When I check the Loki ready endpoint
    Then it should return HTTP 200

  Scenario: Container logs are being ingested from Alloy
    Given the stack has been running for at least 30 seconds
    When I query Loki for '{compose_service=~".+"}'
    Then at least 1 log stream should be returned

  Scenario: LogQL queries return results for specific containers
    When I query Loki for '{compose_service="grafana"}'
    Then the query should return results within 15 seconds
