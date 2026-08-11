"""Validation tests for required CI workflow environment variables."""

from __future__ import annotations

from pathlib import Path

import yaml


def test_acceptance_full_workflow_sets_dora_postgres_url(project_root: Path) -> None:
    """Ensure Acceptance Full workflow can interpolate compose required vars."""
    workflow_path = project_root / ".github" / "workflows" / "ci-acceptance-full.yml"

    with open(workflow_path, encoding="utf-8") as fh:
        workflow = yaml.safe_load(fh)

    env = workflow["jobs"]["acceptance-full"]["env"]
    assert "DORA_POSTGRES_URL" in env, (
        "ci-acceptance-full.yml must set DORA_POSTGRES_URL so docker compose "
        "can interpolate required vars from compose.yaml in CI"
    )
    assert str(env["DORA_POSTGRES_URL"]).strip(), "DORA_POSTGRES_URL must not be empty"
