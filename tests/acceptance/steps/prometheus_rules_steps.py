"""
Step definitions for Prometheus Recording and Alert Rules (OBS-R) feature.

Parses rule YAML files directly from config/prometheus/rules/ for offline testing.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict

import pytest
from pytest_bdd import given, then, when, parsers

from tests.acceptance.runtime import ObservabilityStack


@given('the directory "config/prometheus/rules" exists')
def prometheus_rules_dir_exists(stack: ObservabilityStack) -> None:
    """Assert Prometheus rules directory exists."""
    rules_dir = Path(stack.compose_dir) / "config" / "prometheus" / "rules"
    assert rules_dir.exists() and rules_dir.is_dir(), (
        f"Rules directory not found: {rules_dir}"
    )


def _load_all_rules(stack: ObservabilityStack) -> Dict:
    """Load all rule files from config/prometheus/rules/ and parse them."""
    rules_dir = Path(stack.compose_dir) / "config" / "prometheus" / "rules"
    all_groups = []

    for rule_file in rules_dir.glob("*.yml"):
        content = yaml.safe_load(rule_file.read_text())
        if content and "groups" in content:
            all_groups.extend(content["groups"])

    return {"groups": all_groups}


@when("I load all Prometheus rules")
def load_prometheus_rules(stack: ObservabilityStack) -> None:
    """Load all Prometheus rule files from disk and store in context."""
    rules = _load_all_rules(stack)
    pytest._step_context = {"rules_result": rules}


@then(
    parsers.parse(
        'the directory "config/prometheus/rules" should contain a file matching "{pattern}"'
    )
)
def rules_dir_contains_file(pattern: str, stack: ObservabilityStack) -> None:
    """Assert a rule file exists matching the pattern."""
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
            # Recording rules use "record" field, alerting rules use "name"/"alert"
            rule_name_field = (
                rule.get("record") or rule.get("name") or rule.get("alert")
            )
            if rule_name_field == rule_name:
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
            # Alert rules use "alert" field
            if rule.get("alert") == rule_name:
                found = True
                break
        if found:
            break

    assert found, f"Alert rule '{rule_name}' not found in Prometheus rules"
    print(f"✅ Alert rule '{rule_name}' found")


@then(
    parsers.parse(
        'alert rule "{rule_name}" should have label "{label}" equal to "{value}"'
    )
)
def alert_rule_has_label(
    rule_name: str, label: str, value: str, stack: ObservabilityStack
) -> None:
    """Assert an alert rule has a specific label value."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result", {})
    groups = rules_data.get("groups", [])

    for group in groups:
        for rule in group.get("rules", []):
            if rule.get("alert") == rule_name or rule.get("name") == rule_name:
                rule_labels = rule.get("labels", {})
                assert rule_labels.get(label) == value, (
                    f"Alert rule '{rule_name}' has label '{label}' = '{rule_labels.get(label)}', "
                    f"expected '{value}'"
                )
                print(f"✅ Alert rule '{rule_name}' has label '{label}' = '{value}'")
                return

    pytest.fail(f"Alert rule '{rule_name}' not found")


@then("all recording rules should be guarded with or vector(0)")
def all_recording_rules_guarded() -> None:
    """Assert all recording rules have vector(0) guards."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result", {})
    groups = rules_data.get("groups", [])

    for group in groups:
        for rule in group.get("rules", []):
            # Recording rules have "record" field, alerting rules have "alert" field
            is_recording = "record" in rule

            # Only check recording rules for vector(0) guards
            if is_recording:
                expr = rule.get("expr", "")
                # Check if expression contains vector(0) guard pattern
                has_guard = (
                    "vector(0)" in expr
                    or "or instant_vector(0)" in expr.replace(" ", "")
                )
                assert has_guard, (
                    f"Recording rule '{rule.get('record')}' missing vector(0) guard: {expr}"
                )
    print("✅ All recording rules have appropriate guards")
