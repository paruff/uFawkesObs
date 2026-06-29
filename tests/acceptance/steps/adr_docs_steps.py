"""
Step definitions for ADR and docs sync (M1.5) feature.

Contains a custom step for git tag validation that is not in shared steps.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from pytest_bdd import then, parsers

from tests.acceptance.runtime import ObservabilityStack


@then(parsers.parse('git tag "{tag}" should exist'))
def then_git_tag_exists(stack: ObservabilityStack, tag: str) -> None:
    """Assert that a specific git tag exists in the repository."""
    if not shutil.which("git"):
        pytest.skip("git not available in this environment")
    project_root = stack.compose_dir
    result = subprocess.run(
        ["git", "tag", "-l", tag],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=10,
    )
    tags = result.stdout.strip().splitlines()
    assert tag in tags, f"Git tag '{tag}' not found. Available tags: {tags}"


@then(
    parsers.parse(
        'the version in "{arch_file}" for "{service}" should match compose.yaml'
    )
)
def arch_version_matches_compose(
    arch_file: str, service: str, stack: ObservabilityStack
) -> None:
    """Assert ARCHITECTURE.md version table matches compose.yaml for a service."""
    compose_path = Path(stack.compose_dir) / "compose.yaml"
    compose_content = yaml.safe_load(compose_path.read_text())

    # Get version from compose.yaml
    compose_services = compose_content.get("services", {})
    service_def = compose_services.get(service)
    assert service_def is not None, f"Service '{service}' not found in compose.yaml"
    compose_image = service_def.get("image", "")
    # Extract version from image (e.g., "prom/prometheus:v3.5.4" -> "v3.5.4")
    compose_version = compose_image.split(":")[-1] if ":" in compose_image else ""

    # Get version from ARCHITECTURE.md
    arch_path = Path(arch_file)
    arch_content = arch_path.read_text()

    # Look for service in version table (format: | `prometheus` | ... | v3.5.4 |)
    # Handle backticks in markdown table
    pattern = rf"\|\s*`{re.escape(service)}`\s*\|\s*[^|]*\|\s*([^|]+)\s*\|"
    match = re.search(pattern, arch_content)
    assert match, f"Service '{service}' not found in {arch_file} version table"

    arch_version = match.group(1).strip()
    assert arch_version == compose_version, (
        f"Version mismatch for '{service}': ARCHITECTURE.md has '{arch_version}', "
        f"compose.yaml has '{compose_version}'"
    )
    print(f"✅ Version match for '{service}': {arch_version}")
