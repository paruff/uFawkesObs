@offline @m1
Feature: Core Observability Substrate (M1)
  Validates that the core Docker Compose observability stack is correctly
  configured with pinned versions, healthchecks, and explicit networking.

  Background:
    Given the compose.yaml is loaded

  Scenario: All service images are pinned to specific versions
    Then no service should use the "latest" image tag

  Scenario: All services have healthcheck definitions
    Then all services should have a healthcheck

  Scenario: OTel Collector uses the correct image
    Then service "otel-collector" should have image "otel/opentelemetry-collector-contrib:0.120.0"

  Scenario: Prometheus uses the correct image
    Then service "prometheus" should have image "prom/prometheus:v3.5.4"

  Scenario: Alertmanager uses the correct image
    Then service "alertmanager" should have image "prom/alertmanager:v0.28.0"

  Scenario: Grafana uses the correct image
    Then service "grafana" should have image "grafana/grafana:12.3.7"

  Scenario: Loki uses the correct image
    Then service "loki" should have image "grafana/loki:3.3.2"

  Scenario: Tempo uses the correct image
    Then service "tempo" should have image "grafana/tempo:2.10.5"

  Scenario: Alloy uses the correct image
    Then service "alloy" should have image "grafana/alloy:v1.12.2"

  Scenario: Node Exporter uses the correct image
    Then service "node-exporter" should have image "prom/node-exporter:v1.8.1"

  Scenario: All core services are on the observability network
    Then service "otel-collector" should be in network "observability"
    And service "prometheus" should be in network "observability"
    And service "alertmanager" should be in network "observability"
    And service "grafana" should be in network "observability"
    And service "loki" should be in network "observability"
    And service "tempo" should be in network "observability"
    And service "alloy" should be in network "observability"

  Scenario: Docker compose config validates cleanly
    Then docker compose config should succeed

  Scenario: Docker compose config with core profile validates cleanly
    Then docker compose config with profile "core" should succeed

  Scenario: OTel Collector OTLP receiver is configured
    Given the YAML file "config/otel/collector.yaml" is loaded
    Then the OTel pipeline "metrics" should exist
    And the OTel pipeline "metrics" should contain receiver "otlp"
    And the OTel pipeline "traces" should exist
    And the OTel pipeline "traces" should contain receiver "otlp"
    And the OTel pipeline "logs" should exist
    And the OTel pipeline "logs" should contain receiver "otlp"

  Scenario: Prometheus has a valid configuration file
    Given the YAML file "config/prometheus/prometheus.yaml" is loaded
    Then the YAML should have key "global"
    Then the YAML should have key "scrape_configs"

  Scenario: Grafana datasources are provisioned
    Given the YAML file "config/grafana/provisioning/datasources/datasources.yaml" is loaded
    Then the YAML should have key "datasources"
