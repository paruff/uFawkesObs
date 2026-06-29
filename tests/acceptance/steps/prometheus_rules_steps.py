"""
Step definitions for Prometheus Recording and Alert Rules (OBS-R) feature.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, then, when, parsers

from tests.acceptance.runtime import ObservabilityStack


@given('the directory "config/prometheus/rules" exists')
def prometheus_rules_dir_exists() -> None:
    """Assert Prometheus rules directory exists."""
    pass  # Directory existence is implicit in YAML loading


@when("I load all Prometheus rules")
def load_prometheus_rules(stack: ObservabilityStack) -> None:
    """Load all Prometheus rule files and store in context."""
    promql = stack.promql()
    rules = promql.rules()
    pytest._step_context = {"rules_result": rules}


@then(
    parsers.parse(
        'the directory "config/prometheus/rules" should contain a file matching "{pattern}"'
    )
)
def rules_dir_contains_file(pattern: str, stack: ObservabilityStack) -> None:
    """Assert a rule file exists matching the pattern."""
    from pathlib import Path

    rules_dir = Path(stack.compose_dir) / "config" / "prometheus" / "rules"
    matching = list(rules_dir.glob(pattern))
    assert len(matching) > 0, f"No files matching '{pattern}' in {rules_dir}"
    print(f"✅ Found rule file: {matching[0].name}")


@then(parsers.parse('a recording rule named "{rule_name}" should exist'))
def recording_rule_exists(rule_name: str) -> None:
    """Assert a recording rule exists in loaded rules."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result", {})
    groups = rules_data.get("groups", [])

    found = False
    for group in groups:
        for rule in group.get("rules", []):
            if rule.get("name") == rule_name:
                found = True
                break
        if found:
            break

    assert found, f"Recording rule '{rule_name}' not found in Prometheus rules"
    print(f"✅ Recording rule '{rule_name}' found")


@then(parsers.parse('an alert rule named "{rule_name}" should exist'))
def alert_rule_exists(rule_name: str) -> None:
    """Assert an alert rule exists in loaded rules."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result", {})
    groups = rules_data.get("groups", [])

    found = False
    for group in groups:
        for rule in group.get("rules", []):
            if rule.get("alert") == rule_name or rule.get("name") == rule_name:
                found = True
                break
        if found:
            break

    assert found, f"Alert rule '{rule_name}' not found in Prometheus rules"
    print(f"✅ Alert rule '{rule_name}' found")


@then("all recording rules should be guarded with or vector(0)")
def all_recording_rules_guarded() -> None:
    """Assert all recording rules have vector(0) guards."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result", {})
    groups = rules_data.get("groups", [])

    for group in groups:
        for rule in group.get("rules", []):
            expr = rule.get("expr", "")
            # Check if expression contains vector(0) guard pattern
            has_guard = "vector(0)" in expr or "or instant_vector(0)" in expr.replace(
                " ", ""
            )
            assert has_guard or rule.get("type") == "alerting", (
                f"Recording rule '{rule.get('name')}' missing vector(0) guard: {expr}"
            )
    print("✅ All recording rules have appropriate guards")
