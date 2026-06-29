"""
Step definitions for ADR and docs sync (M1.5) feature.

Contains a custom step for git tag validation that is not in shared steps.
"""

import shutil
import subprocess

import pytest
from pytest_bdd import then, parsers


@then(parsers.parse('git tag "{tag}" should exist'))
def then_git_tag_exists(project_root, tag: str) -> None:
    """Assert that a specific git tag exists in the repository."""
    if not shutil.which("git"):
        pytest.skip("git not available in this environment")
    result = subprocess.run(
        ["git", "tag", "-l", tag],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=10,
    )
    tags = result.stdout.strip().splitlines()
    assert tag in tags, f"Git tag '{tag}' not found. Available tags: {tags}"
