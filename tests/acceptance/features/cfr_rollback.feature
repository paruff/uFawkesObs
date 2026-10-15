@offline @rollback
Feature: CFR-triggered rollback (#502)
  A change-failure-rate regression alert rolls the deploy host back to the
  last verified revision (deploy-latest-good), and does so exactly once.

  Scenario: Firing CFR regression alert rolls the host back
    Given a deploy host running a candidate ahead of deploy-latest-good
    And Prometheus reports DORACFRRegressionRollback as firing
    When the CFR rollback check runs
    Then the host should be on deploy-latest-good
    And the host should have been redeployed and a recovery event sent
    When the CFR rollback check runs
    Then the host should not be redeployed a second time

  Scenario: No firing alert leaves the host untouched
    Given a deploy host running a candidate ahead of deploy-latest-good
    And Prometheus reports DORACFRRegressionRollback as not firing
    When the CFR rollback check runs
    Then the host should still be on the candidate
