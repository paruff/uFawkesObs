"""
Step definitions for Non-Functional Requirements (OBS-N) feature.
"""

from __future__ import annotations

import pytest
import yaml
from pathlib import Path
from pytest_bdd import given, then, when, parsers


@given(parsers.parse('the file "{file_path}" exists'))
def file_exists(file_path: str) -> None:
    """Assert a file exists in the project."""
    p = Path(file_path)
    assert p.exists(), f"File '{file_path}' does not exist"


@when(parsers.parse('I check the content of "{file_path}"'))
def check_file_content(file_path: str) -> None:
    """Read and store file content for assertion."""
    p = Path(file_path)
    if p.exists():
        content = p.read_text()
        pytest._step_context = {"file_content": content, "file_path": file_path}
    else:
        pytest._step_context = {"file_content": "", "file_path": file_path}


@then(parsers.parse('the file "{file_path}" should exist'))
def then_file_exists(file_path: str) -> None:
    """Assert a file exists."""
    p = Path(file_path)
    assert p.exists(), f"File '{file_path}' does not exist"


@then(parsers.parse('it should contain "{text}"'))
def then_contains_text(text: str) -> None:
    """Assert file content contains expected text."""
    ctx = getattr(pytest, "_step_context", {})
    content = ctx.get("file_content", "")
    assert text in content, f"Expected '{text}' not found in file content"
    print(f"✅ File contains '{text}'")


@then(parsers.parse('it should not contain "{text}"'))
def then_not_contains_text(text: str) -> None:
    """Assert file content does not contain forbidden text."""
    ctx = getattr(pytest, "_step_context", {})
    content = ctx.get("file_content", "")
    assert text not in content, f"Unexpected '{text}' found in file content"
    print(f"✅ File does not contain '{text}'")


@given(parsers.parse('the directory "{dir_path}" exists'))
def directory_exists(dir_path: str) -> None:
    """Assert a directory exists."""
    p = Path(dir_path)
    assert p.exists() and p.is_dir(), f"Directory '{dir_path}' does not exist"


@then(
    parsers.parse(
        'the directory "{dir_path}" should contain a file matching "{pattern}"'
    )
)
def directory_contains_matching_file(dir_path: str, pattern: str) -> None:
    """Assert a directory contains at least one file matching pattern."""
    p = Path(dir_path)
    matching = list(p.glob(pattern))
    assert len(matching) > 0, f"No files matching '{pattern}' in '{dir_path}'"
    print(f"✅ Found matching file: {matching[0].name}")


@given(parsers.parse("the compose.yaml is loaded"))
def compose_yaml_loaded() -> None:
    """Compose.yaml is loaded - placeholder for step definition."""
    pass


@then(parsers.parse('the YAML file "{file_path}" is loaded'))
def yaml_file_loaded(file_path: str) -> None:
    """YAML file is loaded - placeholder for step definition."""
    p = Path(file_path)
    assert p.exists(), f"YAML file '{file_path}' does not exist"


@then(parsers.parse('the YAML should have key "{key}"'))
def yaml_has_key(key: str) -> None:
    """Assert YAML has a specific top-level key."""
    ctx = getattr(pytest, "_step_context", {})
    content = ctx.get("file_content", "")
    data = yaml.safe_load(content) if content else {}
    assert key in data, f"Key '{key}' not found in YAML"
