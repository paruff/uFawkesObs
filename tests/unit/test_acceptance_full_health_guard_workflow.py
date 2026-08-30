"""Regression tests for the Acceptance Full health guard workflow."""

from __future__ import annotations

from pathlib import Path

import yaml


def _load_workflow(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        workflow = yaml.safe_load(fh)
    if True in workflow:
        workflow["on"] = workflow.pop(True)
    return workflow


def test_acceptance_full_health_guard_triggers_on_acceptance_full_and_schedule(
    project_root: Path,
) -> None:
    workflow_path = (
        project_root / ".github" / "workflows" / "acceptance-full-health-guard.yml"
    )
    workflow = _load_workflow(workflow_path)

    run = workflow["on"]["workflow_run"]
    assert "Acceptance Full (Post-Merge)" in run["workflows"]
    assert "completed" in run["types"]
    assert "main" in run["branches"]
    assert workflow["on"]["schedule"], "health guard must run on a schedule, too"


def test_acceptance_full_health_guard_can_open_issue_alerts(
    project_root: Path,
) -> None:
    workflow_path = (
        project_root / ".github" / "workflows" / "acceptance-full-health-guard.yml"
    )
    workflow = _load_workflow(workflow_path)

    assert workflow["permissions"]["issues"] == "write"
    step = workflow["jobs"]["acceptance-full-health"]["steps"][0]
    script = step["with"]["script"]
    assert "Acceptance Full (Post-Merge) health guard" in script
    assert "consecutiveFailureThreshold = 2" in script
    assert "alertAfterHours = 24" in script
    assert "github.rest.issues.create" in script
    assert "github.rest.issues.createComment" in script
