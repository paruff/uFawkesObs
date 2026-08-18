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


def test_acceptance_full_workflow_starts_dora_profile(project_root: Path) -> None:
    """OBS-SLI-006 needs dora-api/dora-compute/pushgateway running to have
    any DORA dashboard data at all -- regression test for the 2026-08-18
    investigation (see docs/notes if present, or PR description)."""
    workflow_path = project_root / ".github" / "workflows" / "ci-acceptance-full.yml"

    with open(workflow_path, encoding="utf-8") as fh:
        content = fh.read()

    assert "--profile dora" in content, (
        "ci-acceptance-full.yml must start the dora profile "
        "(docker compose --profile core --profile apps --profile dora up -d) "
        "or DORA dashboards can never have data in this job"
    )


def test_acceptance_full_workflow_sets_short_dora_compute_interval(
    project_root: Path,
) -> None:
    """A short DORA_COMPUTE_INTERVAL_SECONDS gives dora-compute a chance to
    pick up a seeded event within the job's steady-state window, instead of
    only computing once at container start (default interval is 3600s)."""
    workflow_path = project_root / ".github" / "workflows" / "ci-acceptance-full.yml"

    with open(workflow_path, encoding="utf-8") as fh:
        workflow = yaml.safe_load(fh)

    env = workflow["jobs"]["acceptance-full"]["env"]
    assert "DORA_COMPUTE_INTERVAL_SECONDS" in env, (
        "ci-acceptance-full.yml must set a short DORA_COMPUTE_INTERVAL_SECONDS "
        "so a seeded deployment event is picked up before OBS-SLI-006 runs"
    )
    interval = int(env["DORA_COMPUTE_INTERVAL_SECONDS"])
    assert 0 < interval <= 30, (
        f"DORA_COMPUTE_INTERVAL_SECONDS={interval} is too long for the "
        "existing 60s steady-state window to reliably include a recompute"
    )
