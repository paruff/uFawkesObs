"""
Loki log pipeline step definitions.
Additional steps specific to Loki beyond shared steps.
"""

from __future__ import annotations

from pytest_bdd import then, parsers

from tests.acceptance.runtime import ObservabilityStack


@then(parsers.parse('I should see logs with label "{label}"'))
def logs_have_label(stack: ObservabilityStack, label: str) -> None:
    """Assert a label exists in Loki's label inventory."""
    loki = stack.loki()
    labels = loki.labels()
    assert label in labels, f"Label '{label}' not found in Loki: {labels}"
    print(f"✅ Label '{label}' found in Loki")


@then(parsers.parse('the "{label}" label should have values'))
def label_has_values(stack: ObservabilityStack, label: str) -> None:
    """Assert a Loki label has associated values."""
    loki = stack.loki()
    values = loki.label_values(label)
    assert len(values) > 0, f"Label '{label}' has no values"
    print(
        f"✅ Label '{label}' has values: {values[:5]}{'...' if len(values) > 5 else ''}"
    )


@then("Alloy should report active log sources")
def alloy_has_active_sources(stack: ObservabilityStack) -> None:
    """Check Alloy metrics for active Docker log sources."""
    import requests

    resp = requests.get("http://localhost:12345/metrics", timeout=10)
    assert resp.status_code == 200
    # Check for loki source metrics as proxy for active discovery
    has_docker_source = "loki_source_docker" in resp.text
    assert has_docker_source, "Alloy does not report any loki_source_docker metrics"
    print("✅ Alloy has active Docker log sources")
