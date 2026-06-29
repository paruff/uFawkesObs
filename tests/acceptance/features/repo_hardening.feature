@offline @m2 @docs
Feature: Repository Hardening (M2)
  Validates that repository metadata, GitOps standards, and documentation
  are correctly configured as per M2 tasks.

  # --- M2-02: GitOps Standards ---

  Scenario: Dependabot configuration exists with Docker and GitHub Actions ecosystems
    Given the file ".github/dependabot.yml" exists
    When I check the content of ".github/dependabot.yml"
    Then it should contain "docker"
    And it should contain "github-actions"

  Scenario: FUNDING.yml uses array format
    Given the file ".github/FUNDING.yml" exists
    When I check the content of ".github/FUNDING.yml"
    Then it should contain "github: ["
    And it should contain "paruff"

  Scenario: CHANGELOG.md exists in Keep a Changelog format
    Given the file "CHANGELOG.md" exists
    When I check the content of "CHANGELOG.md"
    Then it should contain "Keep a Changelog"

  Scenario: CODEOWNERS file exists
    Then the file ".github/CODEOWNERS" should exist

  Scenario: v0.1.0 tag exists in git
    Then git tag "v0.1.0" should exist

  # --- M2-03: Platform Documentation ---

  Scenario: ARCHITECTURE.md exists and is valid markdown
    Then the file "docs/ARCHITECTURE.md" should exist

  Scenario: KNOWN_LIMITATIONS.md exists
    Then the file "docs/KNOWN_LIMITATIONS.md" should exist

  Scenario: CHANGE_IMPACT_MAP.md exists
    Then the file "docs/CHANGE_IMPACT_MAP.md" should exist

  # --- M2-04: Repository Metadata ---

  Scenario: README.md includes a CI badge
    Given the file "README.md" exists
    When I check the content of "README.md"
    Then it should contain "github.com/paruff/uFawkesObs/actions"
