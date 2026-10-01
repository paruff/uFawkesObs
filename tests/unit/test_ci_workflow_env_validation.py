"""Validation tests for required CI workflow environment variables."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


def _walk(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key, value
            yield from _walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item)


def test_workflows_pin_runner_images(project_root: Path) -> None:
    """All GitHub-hosted workflow jobs must use pinned runner images."""
    workflow_dir = project_root / ".github" / "workflows"
    for workflow_path in sorted(workflow_dir.glob("*.yml")) + sorted(
        workflow_dir.glob("*.yaml")
    ):
        text = workflow_path.read_text(encoding="utf-8")
        assert "ubuntu-latest" not in text, (
            f"{workflow_path.name} still uses ubuntu-latest; pin runner images to a fixed image like ubuntu-24.04"
        )


def test_workflows_pin_python_patch_versions(project_root: Path) -> None:
    """Python setup steps must use exact patch-version pins, not floating minors."""
    workflow_dir = project_root / ".github" / "workflows"
    for workflow_path in sorted(workflow_dir.glob("*.yml")) + sorted(
        workflow_dir.glob("*.yaml")
    ):
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        for key, value in _walk(workflow):
            if key == "python-version" and isinstance(value, str):
                assert re.fullmatch(r"\d+\.\d+\.\d+", value), (
                    f"{workflow_path.name} sets python-version={value!r}, which is not an exact patch version"
                )


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


def test_make_up_starts_demo_app_profile(project_root: Path) -> None:
    """README Quick Start must reach a real signal path without a hidden extra step.

    `make up` is the default command users follow on a clean host. It must
    include the demo app profile, or Grafana never receives the live metrics,
    logs, and traces the release gate expects.
    """
    makefile = project_root / "Makefile"
    content = makefile.read_text(encoding="utf-8")

    lines = content.splitlines()
    up_index = next(i for i, line in enumerate(lines) if line.startswith("up:"))
    up_target_lines = []
    for line in lines[up_index + 1 :]:
        if not line.strip():
            break
        if line.startswith("\t"):
            up_target_lines.append(line)
            continue
        if line.startswith("## "):
            continue
        if line.endswith(":") and not line.startswith("\t"):
            break
        up_target_lines.append(line)

    command = "\n".join(up_target_lines)

    assert "--profile core" in command, "make up must include the core profile"
    assert "--profile apps" in command, (
        "make up must include the demo app profile so a fresh quick-start run "
        "emits metrics, logs, and traces without an undocumented extra command"
    )
