@offline @prometheus @rules
Feature: Prometheus Recording and Alert Rules
  Validates that all Prometheus rule files in config/prometheus/rules/
  comply with uFawkesObs conventions: vector(0) guards, absent() companions,
  correct structure, and valid YAML.

  Background:
    When I load all Prometheus rules

  Scenario: Self-monitoring rule file exists
    Given the directory "config/prometheus/rules" exists
    Then the directory "config/prometheus/rules" should contain a file matching "ufawkesobs-self-monitoring.yml"

  Scenario: AI rules file exists
    Given the directory "config/prometheus/rules" exists
    Then the directory "config/prometheus/rules" should contain a file matching "ai-rules.yml"

  Scenario: All recording rules are guarded with or vector(0)
    Then all recording rules should be guarded with or vector(0)

  Scenario: Self-monitoring alert rules are defined
    Then an alert rule named "UFawkesObsServiceDown" should exist
    And an alert rule named "UFawkesObsPrometheusStorageHigh" should exist
    And an alert rule named "UFawkesObsLokiIngestionDropped" should exist
    And an alert rule named "UFawkesObsTempoStorageHigh" should exist
    And an alert rule named "UFawkesObsOtelCollectorDropped" should exist
    And an alert rule named "UFawkesObsContainerRestarting" should exist

  Scenario: Self-monitoring alerts have critical severity for service down
    Then alert rule "UFawkesObsServiceDown" should have label "severity" equal to "critical"

  Scenario: Self-monitoring alerts have correct alert domain labels
    Then alert rule "UFawkesObsServiceDown" should have label "alert_domain" equal to "ufawkesobs-health"
    And alert rule "UFawkesObsOtelCollectorDropped" should have label "alert_domain" equal to "ufawkesobs-health"

  Scenario: AI capability alerts have category label
    Then alert rule "AILLMLatencyHigh" should have label "category" equal to "ai-capability"
    And alert rule "AITokenBudgetHigh" should have label "category" equal to "ai-capability"

  Scenario: AI capability alerts have absent companion guards
    Then an alert rule named "AILLMLatencyHighAbsent" should exist
    And an alert rule named "AITokenBudgetHighAbsent" should exist
    And an alert rule named "AIReworkRateHighAbsent" should exist
    And an alert rule named "AIReworkRateCriticalAbsent" should exist
