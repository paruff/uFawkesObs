@offline @specification @nfr
Feature: Non-Functional Requirements (OBS-N)
  Validates the non-functional requirements defined in specification.md

  Scenario: OBS-N01 — Unit test suite validates configuration files
    Then the directory "tests/unit" should contain a file matching "test_*_config_*.py"

  Scenario: OBS-N04 — No credentials in source or config files
    Given the file "compose.yaml" exists
    When I check the content of "compose.yaml"
    Then it should not contain "password:"
    And it should not contain "api_key:"
    And it should not contain "secret_key:"

  Scenario: OBS-N05 — All images are pinned to precise versions
    Given the compose.yaml is loaded
    Then no service should use the "latest" image tag
