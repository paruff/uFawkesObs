"""
Step definitions for Repository Hardening (M2) feature.
"""

from __future__ import annotations

import pytest
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from pytest_bdd import given, then, when, parsers

if TYPE_CHECKING:
    from tests.acceptance.runtime import ObservabilityStack


@given("the file '.github/dependabot.yml' exists")
def dependabot_yaml_exists() -> None:
    """Assert Dependabot config exists."""
    p = Path(".github/dependabot.yml")
    assert p.exists(), "Repository requires Dependabot configuration"


@when(parsers.parse('I check the content of ".github/dependabot.yml"'))
def check_dependabot_content() -> None:
    """Read Dependabot config for required patterns."""
    p = Path(".github/dependabot.yml")
    content = p.read_text()
    pytest._step_context = {"content": content}


@then("the Dependabot config should contain 'docker'")
def has_docker_in_dependabot():
    """Dependabot must monitor Docker-related files."""
    content = getattr(pytest, "_step_context", {}).get("content", "")
    assert "docker" in content, "Dependabot config missing Docker references"


@then("the Dependabot config should contain 'github-actions'")
def has_github_actions_in_dependabot():
    """Dependabot must monitor GitHub Actions workflows."""
    content = getattr(pytest, "_step_context", {}).get("content", "")
    assert "github-actions" in content, (
        "Dependabot config missing GitHub Actions references"
    )


@given("the file '.github/FUNDING.yml' exists")
def funding_yaml_exists() -> None:
    """Assert FUNDING.yml exists."""
    p = Path(".github/FUNDING.yml")
    assert p.exists(), "Repository requires FUNDING.yml for funding sources"


@given("the file '.github/CODEOWNERS' exists")
def codeowners_exists() -> None:
    """Assert CODEOWNERS file exists."""
    p = Path(".github/CODEOWNERS")
    assert p.exists(), "Repository requires CODEOWNERS file"


@then(parsers.parse('git tag "{tag}" should exist'))
def git_tag_exists(tag: str, stack: "ObservabilityStack") -> None:
    """Assert a specific git tag exists."""
    project_root = stack.compose_dir if stack else Path(".")
    result = subprocess.run(
        ["git", "rev-parse", tag],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Git tag '{tag}' does not exist: {result.stderr}"


@then(parsers.parse('the file "CHANGELOG.md" should exist'))
def changelog_exists() -> None:
    """Assert CHANGELOG.md exists."""
    p = Path("CHANGELOG.md")
    assert p.exists(), "CHANGELOG.md is missing"


@then(parsers.parse('the file "CHANGELOG.md" should contain "Keep a Changelog"'))
def changelog_keep_changelog() -> None:
    """Assert CHANGELOG.md follows Keep a Changelog format."""
    p = Path("CHANGELOG.md")
    content = p.read_text()
    assert "Keep a Changelog" in content, (
        "CHANGELOG.md doesn't start with 'Keep a Changelog'"
    )


@given(parsers.parse('the file "ARCHITECTURE.md" exists'))
def readme_exists() -> None:
    """Assert ARCHITECTURE.md exists."""
    p = Path("docs/ARCHITECTURE.md")
    assert p.exists(), "ARCHITECTURE.md is missing"


then_existing_file = given("the file '{file_path}' exists")


@given("the file 'docs/KNOWN_LIMITATIONS.md' exists")
def known_limits_exists() -> None:
    """Assert KNOWN_LIMITATIONS.md exists."""
    p = Path("docs/KNOWN_LIMITATIONS.md")
    assert p.exists(), "KNOWN_LIMITATIONS.md is missing"


@given("the file 'docs/CHANGE_IMPACT_MAP.md' exists")
def change_impact_map_exists() -> None:
    """Assert CHANGE_IMPACT_MAP.md exists."""
    p = Path("docs/CHANGE_IMPACT_MAP.md")
    assert p.exists(), "CHANGE_IMPACT_MAP.md is missing"


# Steps for Repository Metadata


@then(
    parsers.parse(
        'the file "README.md" should contain "github.com/paruff/uFawkesObs/actions"'
    )
)
def readme_has_controls_badge() -> None:
    """Assert README.md contains CI badge."""
    p = Path("README.md")
    content = p.read_text()
    assert "github.com/paruff/uFawkesObs/actions" in content, (
        "README.md missing CI badge"
    )

    print("✅ README.md contains CI badge")
