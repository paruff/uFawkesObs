@offline @m1.5 @adr
Feature: ADR and Docs Sync (M1.5)
  Validates that Architecture Decision Records, ARCHITECTURE.md, and
  the obs-stack skill file all reflect the current service versions.

  # --- M1.5-01: ADR-001 Loki Version ---

  Scenario: ADR-001 references Loki 3.3.2
    Given the file "docs/adr/ADR-001-loki-version.md" exists
    When I check the content of "docs/adr/ADR-001-loki-version.md"
    Then it should contain "3.3.2"

  Scenario: ADR-001 contains schema v13 reference (not v11)
    When I check the content of "docs/adr/ADR-001-loki-version.md"
    Then it should contain "v13"
    And it should not contain "boltdb"

  # --- M1.5-01: ADR-004 Grafana 12 ---

  Scenario: ADR-004 for Grafana 12 migration exists
    Then the file "docs/adr/ADR-004-grafana-12x-migration.md" should exist

  Scenario: ADR-004 references Grafana 12.3.7
    Given the file "docs/adr/ADR-004-grafana-12x-migration.md" exists
    When I check the content of "docs/adr/ADR-004-grafana-12x-migration.md"
    Then it should contain "12.3.7"

  # --- M1.5-02: ARCHITECTURE.md version sync ---

  Scenario: ARCHITECTURE.md version table matches compose.yaml for Prometheus
    Given the compose.yaml is loaded
    Then the version in "docs/ARCHITECTURE.md" for "prometheus" should match compose.yaml

  Scenario: ARCHITECTURE.md version table matches compose.yaml for Loki
    Given the compose.yaml is loaded
    Then the version in "docs/ARCHITECTURE.md" for "loki" should match compose.yaml

  Scenario: ARCHITECTURE.md version table matches compose.yaml for Grafana
    Given the compose.yaml is loaded
    Then the version in "docs/ARCHITECTURE.md" for "grafana" should match compose.yaml

  # --- M1.5-03: obs-stack SKILL.md version sync ---

  Scenario: obs-stack SKILL.md references correct Prometheus version
    Given the file ".agents/skills/obs-stack/SKILL.md" exists
    When I check the content of ".agents/skills/obs-stack/SKILL.md"
    Then it should contain "v3.5.4"

  Scenario: obs-stack SKILL.md references correct Loki version
    When I check the content of ".agents/skills/obs-stack/SKILL.md"
    Then it should contain "3.3.2"

  Scenario: obs-stack SKILL.md references correct Grafana version
    When I check the content of ".agents/skills/obs-stack/SKILL.md"
    Then it should contain "12.3.7"

  # --- ADR index ---

  Scenario: ADR README.md index exists
    Then the file "docs/adr/README.md" should exist

  Scenario: ADR README.md lists ADR-004
    Given the file "docs/adr/README.md" exists
    When I check the content of "docs/adr/README.md"
    Then it should contain "ADR-004"

  Scenario: ADR README.md lists ADR-005
    When I check the content of "docs/adr/README.md"
    Then it should contain "ADR-005"
