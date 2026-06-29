"""
Step definitions for AI Observability Pipeline (OBS-AI) feature.
"""

from __future__ import annotations

import pytest
import yaml
from pathlib import Path
from pytest_bdd import then, parsers

from tests.acceptance.runtime import ObservabilityStack


@then(parsers.parse('the OTel pipeline "{pipeline_name}" should exist'))
def otel_pipeline_exists(pipeline_name: str, stack: ObservabilityStack) -> None:
    """Assert an OTel pipeline exists in the collector config."""
    collector_path = Path(stack.compose_dir) / "config" / "otel" / "collector.yaml"
    content = yaml.safe_load(collector_path.read_text())

    pipelines = content.get("service", {}).get("pipelines", {})
    assert pipeline_name in pipelines, (
        f"Pipeline '{pipeline_name}' not found in OTel config"
    )
    print(f"✅ Pipeline '{pipeline_name}' exists in OTel Collector config")


@then(
    parsers.parse(
        'the OTel pipeline "{pipeline_name}" should contain receiver "{receiver}"'
    )
)
def otel_pipeline_has_receiver(
    pipeline_name: str, receiver: str, stack: ObservabilityStack
) -> None:
    """Assert an OTel pipeline contains a specific receiver."""
    collector_path = Path(stack.compose_dir) / "config" / "otel" / "collector.yaml"
    content = yaml.safe_load(collector_path.read_text())

    pipelines = content.get("service", {}).get("pipelines", {})
    pipeline = pipelines.get(pipeline_name, {})
    receivers = pipeline.get("receivers", [])

    assert receiver in receivers, (
        f"Receiver '{receiver}' not in pipeline '{pipeline_name}'"
    )
    print(f"✅ Pipeline '{pipeline_name}' has receiver '{receiver}'")


@then(
    parsers.parse(
        'the OTel pipeline "{pipeline_name}" should contain processor "{processor}"'
    )
)
def otel_pipeline_has_processor(
    pipeline_name: str, processor: str, stack: ObservabilityStack
) -> None:
    """Assert an OTel pipeline contains a specific processor."""
    collector_path = Path(stack.compose_dir) / "config" / "otel" / "collector.yaml"
    content = yaml.safe_load(collector_path.read_text())

    pipelines = content.get("service", {}).get("pipelines", {})
    pipeline = pipelines.get(pipeline_name, {})
    processors = pipeline.get("processors", [])

    assert processor in processors, (
        f"Processor '{processor}' not in pipeline '{pipeline_name}'"
    )
    print(f"✅ Pipeline '{pipeline_name}' has processor '{processor}'")


@then(
    parsers.parse(
        'the OTel pipeline "{pipeline_name}" should contain exporter "{exporter}"'
    )
)
def otel_pipeline_has_exporter(
    pipeline_name: str, exporter: str, stack: ObservabilityStack
) -> None:
    """Assert an OTel pipeline contains a specific exporter."""
    collector_path = Path(stack.compose_dir) / "config" / "otel" / "collector.yaml"
    content = yaml.safe_load(collector_path.read_text())

    pipelines = content.get("service", {}).get("pipelines", {})
    pipeline = pipelines.get(pipeline_name, {})
    exporters = pipeline.get("exporters", [])

    assert exporter in exporters, (
        f"Exporter '{exporter}' not in pipeline '{pipeline_name}'"
    )
    print(f"✅ Pipeline '{pipeline_name}' has exporter '{exporter}'")


@then(
    parsers.parse(
        'alert rule "{rule_name}" should have label "{label}" equal to "{value}"'
    )
)
def alert_rule_has_label(
    rule_name: str, label: str, value: str, stack: ObservabilityStack
) -> None:
    """Assert an alert rule has a specific label value."""
    promql = stack.promql()
    rules = promql.rules()
    groups = rules.get("groups", [])

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
