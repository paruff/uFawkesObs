"""
Unit tests guarding the LB-04 rollback drill documentation (#182).

These tests lock in that the rollback drill runbook exists, covers the
required phases (preconditions, bad-deploy recipe, procedure, evidence,
results, safety), and that the deployment strategy document links it and
does NOT claim the rollback path is proven until the drill records results.

Run:  pytest tests/unit/test_deploy_docs.py -v
      (no running stack required — reads docs statically)
"""

from __future__ import annotations

import pathlib

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
ROLLBACK_DRILL = PROJECT_ROOT / "docs" / "ROLLBACK_DRILL.md"
DEPLOYMENT_STRATEGY = PROJECT_ROOT / "docs" / "DEPLOYMENT_STRATEGY.md"

REQUIRED_RUNBOOK_SECTIONS: tuple[str, ...] = (
    "## Preconditions",
    "## Bad-Deploy Recipe",
    "## Drill Procedure",
    "## Evidence Log",
    "## Results & Follow-Up",
    "## Safety & Cleanup",
)


@pytest.fixture(scope="module")
def rollback_drill_text() -> str:
    """Return the rollback drill runbook contents."""
    if not ROLLBACK_DRILL.exists():
        pytest.fail(f"Rollback drill runbook not found at {ROLLBACK_DRILL}")
    return ROLLBACK_DRILL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def deployment_strategy_text() -> str:
    """Return the deployment strategy document contents."""
    if not DEPLOYMENT_STRATEGY.exists():
        pytest.fail(f"Deployment strategy not found at {DEPLOYMENT_STRATEGY}")
    return DEPLOYMENT_STRATEGY.read_text(encoding="utf-8")


class TestRollbackDrillRunbook:
    """Verify the runbook exists and covers every drill phase."""

    @pytest.mark.parametrize(
        "heading", REQUIRED_RUNBOOK_SECTIONS, ids=REQUIRED_RUNBOOK_SECTIONS
    )
    def test_runbook_has_required_section(
        self, rollback_drill_text: str, heading: str
    ) -> None:
        """Assert the runbook contains each required phase heading."""
        assert heading in rollback_drill_text, (
            f"Rollback drill runbook is missing required section '{heading}'"
        )

    def test_runbook_defines_success_criteria(self, rollback_drill_text: str) -> None:
        """Assert the drill defines how success is judged."""
        assert "success" in rollback_drill_text.lower(), (
            "Rollback drill runbook must define success criteria"
        )

    def test_runbook_provides_evidence_template(self, rollback_drill_text: str) -> None:
        """Assert the runbook gives a concrete evidence log template."""
        assert "Evidence" in rollback_drill_text
        assert "Workflow run: https://" in rollback_drill_text, (
            "Evidence template must reference the GitHub workflow run URL to record"
        )


class TestRollbackDrillTagBasedDesign:
    """Verify the runbook documents the tag-based deploy/rollback redesign.

    Rollback checks out the ``deploy-latest-good`` tag on the host instead of
    ``git revert`` + pushing to ``main`` — this is what makes the drill immune
    to main's branch protection (the original #193/#182 concern).
    """

    def test_runbook_documents_deploy_latest_good_tag(
        self, rollback_drill_text: str
    ) -> None:
        assert "deploy-latest-good" in rollback_drill_text, (
            "Runbook must document the deploy-latest-good tag rollback targets"
        )

    def test_runbook_confirms_rollback_never_pushes_to_main(
        self, rollback_drill_text: str
    ) -> None:
        assert "does not push to main" in rollback_drill_text.lower() or (
            "never push" in rollback_drill_text.lower()
        ), (
            "Runbook must state that rollback never pushes to main, since "
            "that's what makes it immune to branch protection"
        )

    def test_runbook_no_longer_names_branch_protection_as_a_blocker(
        self, rollback_drill_text: str
    ) -> None:
        assert "cannot run as automated" not in rollback_drill_text, (
            "Tag-based rollback never pushes to main, so branch protection "
            "can no longer block the drill — this stale caveat must be removed"
        )


class TestDeploymentStrategyRollbackSection:
    """Verify the deployment strategy links the drill and does not overclaim."""

    def test_strategy_references_runbook(self, deployment_strategy_text: str) -> None:
        """Assert the strategy document links the rollback drill runbook."""
        assert "ROLLBACK_DRILL.md" in deployment_strategy_text, (
            "Deployment strategy must link docs/ROLLBACK_DRILL.md in its "
            "rollback section"
        )

    def test_strategy_does_not_claim_rollback_is_proven(
        self, deployment_strategy_text: str
    ) -> None:
        """Assert the strategy does not present the rollback as verified."""
        assert "ROLLBACK_DRILL.md" in deployment_strategy_text
        assert (
            "unproven" in deployment_strategy_text.lower()
            or "not yet" in deployment_strategy_text.lower()
        ), (
            "Deployment strategy must not claim the rollback path is proven — "
            "LB-04 drill results are still PENDING"
        )
