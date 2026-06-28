@offline @ai @m-ai
Feature: AI Observability Pipeline (OBS-AI)
  Validates that the AI metrics pipeline, recording rules, and alerting
  are correctly configured in the OTel Collector and Prometheus.

  Background:
    Given the YAML file "config/otel/collector.yaml" is loaded

  # --- OBS-AI-01: OTel AI Metrics Pipeline ---

  Scenario: The AI metrics pipeline exists in the OTel Collector
    Then the OTel pipeline "metrics/ai" should exist

  Scenario: The AI metrics pipeline uses the OTLP receiver
    Then the OTel pipeline "metrics/ai" should contain receiver "otlp"

  Scenario: The AI metrics pipeline includes the filter/ai processor
    Then the OTel pipeline "metrics/ai" should contain processor "filter/ai"

  Scenario: The AI metrics pipeline includes the attributes/ai processor
    Then the OTel pipeline "metrics/ai" should contain processor "attributes/ai"

  Scenario: The AI metrics pipeline exports to Prometheus
    Then the OTel pipeline "metrics/ai" should contain exporter "prometheus"

  Scenario: Existing pipelines are unchanged when AI pipeline is added
    Then the OTel pipeline "metrics" should exist
    And the OTel pipeline "metrics" should contain receiver "otlp"
    And the OTel pipeline "traces" should exist
    And the OTel pipeline "logs" should exist

  # --- OBS-AI-02: Prometheus AI Recording Rules ---

  Scenario: AI recording rules file exists
    Given the directory "config/prometheus/rules" exists
    Then the directory "config/prometheus/rules" should contain a file matching "ai-rules.yml"

  Scenario: AI latency recording rules are defined
    When I load all Prometheus rules
    Then a recording rule named "ai:llm_request_latency_p99:seconds" should exist
    And a recording rule named "ai:llm_request_latency_p50:seconds" should exist

  Scenario: AI token usage recording rule is defined
    When I load all Prometheus rules
    Then a recording rule named "ai:token_usage_rate:per_minute" should exist

  Scenario: AI acceptance rate recording rule is defined
    When I load all Prometheus rules
    Then a recording rule named "ai:suggestion_acceptance_rate:ratio" should exist

  Scenario: All AI recording rules are guarded with or vector(0)
    When I load all Prometheus rules
    Then all recording rules should be guarded with or vector(0)

  Scenario: AI alert rules are defined
    When I load all Prometheus rules
    Then an alert rule named "AILLMLatencyHigh" should exist
    And an alert rule named "AITokenBudgetHigh" should exist

  Scenario: AI alert rules have absent() companion guards
    When I load all Prometheus rules
    Then an alert rule named "AILLMLatencyHighAbsent" should exist
    And an alert rule named "AITokenBudgetHighAbsent" should exist

  Scenario: AI alert rules have correct severity labels
    When I load all Prometheus rules
    Then alert rule "AILLMLatencyHigh" should have label "severity" equal to "warning"
    And alert rule "AITokenBudgetHigh" should have label "severity" equal to "warning"
