"""
OTel Collector and Prometheus step definitions.
Additional steps specific to the OTel pipeline beyond shared steps.
"""

from __future__ import annotations

import pytest
from pytest_bdd import when, then

from tests.acceptance.runtime import ObservabilityStack


@when("I send a test metric via OTLP")
def send_test_metric(stack: ObservabilityStack) -> None:
    """Send a synthetic counter metric via OTLP HTTP."""
    otlp = stack.otlp()
    test_id = otlp.send_counter("smoke_test_counter", value=42.0)
    pytest._step_context = {"test_metric_id": test_id}


@then("the metric should appear in Prometheus within 30 seconds")
def metric_in_prometheus(stack: ObservabilityStack) -> None:
    """Poll Prometheus until the test metric appears."""

    ctx = getattr(pytest, "_step_context", {})
    test_id = ctx.get("test_metric_id")
    assert test_id is not None, "No test metric ID in context"

    promql = stack.promql()
    found, elapsed, data = promql.poll_metric(
        f'smoke_test_counter_total{{test_id="{test_id}"}}',
        timeout=30,
    )
    assert found, "Test metric not found in Prometheus within 30s"
    print(f"✅ Metric found after {elapsed:.1f}s: {data}")


@then("the trace should be queryable in Tempo")
def trace_in_tempo(stack: ObservabilityStack) -> None:
    """Poll Tempo until the test trace appears."""

    ctx = getattr(pytest, "_step_context", {})
    trace_id = ctx.get("test_trace_id")
    assert trace_id is not None, "No test trace ID in context"

    tempo = stack.tempo()
    found, elapsed, data = tempo.poll_trace(trace_id, timeout=30)
    assert found, f"Test trace {trace_id} not found in Tempo within 30s"
    print(f"✅ Trace found after {elapsed:.1f}s")
