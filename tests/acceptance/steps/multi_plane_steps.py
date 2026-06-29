"""
Multi-Plane Contract Step Definitions (OBS-CONTRACT-001-004).

Step implementations for cross-plane telemetry contract scenarios:
  - OBS-CONTRACT-001: External OTLP trace → Tempo
  - OBS-CONTRACT-002: External OTLP metric → Prometheus
  - OBS-CONTRACT-003: External OTLP log → Loki
  - OBS-CONTRACT-004: Cross-plane datasource resolution

Each scenario simulates an external plane joining the ``observability-lab``
network, sending OTLP telemetry, and verifying it arrives in the respective
backend service via direct API queries (not through Grafana).
"""

from __future__ import annotations

import json
import time
from typing import Any

import pytest
from pytest_bdd import then, when, parsers

from tests.acceptance.runtime import ObservabilityStack
from tests.acceptance.workloads.synthetic_trace import SyntheticTraceWorkload
from tests.acceptance.workloads.synthetic_metric import SyntheticMetricWorkload
from tests.acceptance.workloads.synthetic_log import SyntheticLogWorkload

# ── Constants ──────────────────────────────────────────────────────────

OTLP_HTTP = "http://localhost:4318"
OTLP_GRPC = "localhost:4317"

SERVICE_NAME = "acceptance-test-plane"

# ── Helpers ────────────────────────────────────────────────────────────


def _normalize_datasource_url(url: str) -> str:
    """Normalise a Grafana datasource URL for comparison.

    Strips trailing slashes and protocol prefixes for robust matching.
    """
    url = url.rstrip("/")
    for prefix in ["http://", "https://"]:
        if url.startswith(prefix):
            url = url[len(prefix) :]
    return url


# ── OBS-CONTRACT-001: Trace Contract ───────────────────────────────────


@when("an external plane sends a synthetic OTLP trace via gRPC")
def send_contract_trace(stack: ObservabilityStack) -> None:
    """Send a synthetic trace via OTLP gRPC and store the trace_id."""
    workload = SyntheticTraceWorkload(
        otlp_endpoint=OTLP_GRPC,
        protocol="grpc",
        service_name=SERVICE_NAME,
    )
    trace_id = workload.simulate_web_request(
        extra_attrs={"contract": "obs-contract-001"}
    )
    print(f"🔍 Sent contract trace: {trace_id}")
    pytest._step_context = {
        "contract_trace_id": trace_id,
        "contract_trace_sent_at": time.time(),
    }


@then("the trace should be queryable via Tempo API within 15 seconds")
def trace_queryable_in_tempo(stack: ObservabilityStack) -> None:
    """Poll Tempo until the trace appears."""
    ctx = getattr(pytest, "_step_context", {})
    trace_id = ctx.get("contract_trace_id")
    assert trace_id is not None, "No contract_trace_id in step context"

    tempo = stack.tempo()
    found, elapsed, data = tempo.poll_trace(trace_id, timeout=15)
    assert found, f"Contract trace {trace_id} not found in Tempo within 15s"
    print(f"✅ Contract trace found in Tempo after {elapsed:.1f}s")
    pytest._step_context["contract_trace_data"] = data


@then("the trace should have at least 3 spans preserved")
def trace_has_min_spans() -> None:
    """Assert the trace has at least 3 spans."""
    ctx = getattr(pytest, "_step_context", {})
    data = ctx.get("contract_trace_data")
    assert data is not None, "No trace data in step context"

    # Tempo returns traces in various formats
    spans = []
    if "batches" in data:
        for batch in data["batches"]:
            if "scopeSpans" in batch:
                for scope_span in batch["scopeSpans"]:
                    spans.extend(scope_span.get("spans", []))
            elif "instrumentationLibrarySpans" in batch:
                for lib_span in batch["instrumentationLibrarySpans"]:
                    spans.extend(lib_span.get("spans", []))

    count = len(spans)
    assert count >= 3, f"Expected >= 3 spans, got {count}"
    print(f"✅ Trace has {count} spans preserved")


# ── OBS-CONTRACT-002: Metric Contract ──────────────────────────────────


@when(
    parsers.parse(
        'an external plane sends a counter metric "{metric_name}" with value {value:d}'
    )
)
def send_contract_metric(
    stack: ObservabilityStack, metric_name: str, value: int
) -> None:
    """Send a counter metric via OTLP HTTP and store the test_id."""
    workload = SyntheticMetricWorkload(
        otlp_http_endpoint=OTLP_HTTP,
        service_name=SERVICE_NAME,
    )
    test_id = workload.emit_counter(
        metric_name,
        value=float(value),
        labels={"contract": "obs-contract-002"},
    )
    print(f"📊 Sent contract metric '{metric_name}' = {value}, test_id={test_id}")
    pytest._step_context = {
        "contract_metric_name": metric_name,
        "contract_metric_value": value,
        "contract_test_id": test_id,
        "contract_metric_sent_at": time.time(),
    }


@then("the metric should appear in Prometheus within 30 seconds")
def metric_in_prometheus(stack: ObservabilityStack) -> None:
    """Poll Prometheus until the metric appears."""
    ctx = getattr(pytest, "_step_context", {})
    metric_name = ctx.get("contract_metric_name")
    test_id = ctx.get("contract_test_id")
    assert metric_name, "No contract_metric_name in step context"
    assert test_id, "No contract_test_id in step context"

    # OTel Collector's Prometheus exporter adds "app_metrics_" prefix and "_total" suffix
    prometheus_metric = f"app_metrics_{metric_name}_total"
    promql = stack.promql()
    found, elapsed, data = promql.poll_metric(
        f'{prometheus_metric}{{test_id="{test_id}"}}',
        timeout=30,
    )
    assert found, (
        f"Metric {prometheus_metric} with test_id={test_id} "
        f"not found in Prometheus within 30s"
    )
    print(f"✅ Contract metric found in Prometheus after {elapsed:.1f}s: {data}")
    pytest._step_context["contract_metric_data"] = data


@then('the metric should have labels: "test_id", "service_name"')
def metric_has_labels() -> None:
    """Assert the metric has expected labels."""
    ctx = getattr(pytest, "_step_context", {})
    data = ctx.get("contract_metric_data")
    assert data is not None, "No metric data in step context"

    metric = data.get("metric", {})
    assert "test_id" in metric, "Metric missing 'test_id' label"
    assert "service_name" in metric or "service" in metric, (
        "Metric missing service label"
    )
    print(
        f"✅ Metric has labels: test_id={metric.get('test_id')}, "
        f"service_name={metric.get('service_name') or metric.get('service')}"
    )


# ── OBS-CONTRACT-003: Log Contract ─────────────────────────────────────


@when("an external plane sends a structured JSON log via OTLP logs signal")
def send_contract_log(stack: ObservabilityStack) -> None:
    """Send a structured JSON log via OTLP and store the test_id."""
    workload = SyntheticLogWorkload(
        otlp_http_endpoint=OTLP_HTTP,
        service_name=SERVICE_NAME,
    )
    test_id = workload.emit_log(
        body={
            "event": "contract_test",
            "contract": "obs-contract-003",
            "message": "External plane log entry",
            "severity": "info",
            "service": SERVICE_NAME,
        },
        severity_text="INFO",
        extra_attributes={"contract": "obs-contract-003"},
    )
    print(f"📝 Sent contract log, test_id={test_id}")
    pytest._step_context = {
        "contract_log_test_id": test_id,
        "contract_log_sent_at": time.time(),
    }


@then("the log should be queryable in Loki within 20 seconds")
def log_queryable_in_loki(stack: ObservabilityStack) -> None:
    """Poll Loki until the log entry appears."""
    ctx = getattr(pytest, "_step_context", {})
    test_id = ctx.get("contract_log_test_id")
    assert test_id is not None, "No contract_log_test_id in step context"

    # test_id is in the log body (not a Loki label), so we use line filtering
    query = '{compose_service="otel-collector"} |= "test_id=' + test_id + '"'
    loki = stack.loki()
    start = time.time()
    found = False
    result_data: dict[str, Any] = {}

    while time.time() - start < 20:
        result = loki.query_range(query, limit=10)
        streams = result.get("data", {}).get("result", [])
        if streams:
            found = True
            result_data = result
            elapsed = time.time() - start
            print(f"✅ Contract log found in Loki after {elapsed:.1f}s")
            break
        time.sleep(2)

    assert found, f"Log with test_id={test_id} not found in Loki within 20s"
    pytest._step_context["contract_log_result"] = result_data


@then("the log body should parse as valid JSON with the original keys preserved")
def log_body_is_valid_json() -> None:
    """Assert the log body is valid JSON with expected structure.

    The OTel Collector debug exporter produces log lines in the format:
        timestamp\\tlevel\\t{json_body}\\tkey=value key=value

    This step extracts the JSON portion from the log line, ignoring
    the logfmt-style key=value pairs that follow.
    """
    ctx = getattr(pytest, "_step_context", {})
    result = ctx.get("contract_log_result")
    assert result is not None, "No log result in step context"

    streams = result.get("data", {}).get("result", [])
    assert streams, "No log streams in result"

    # Check first stream's first entry for parseable JSON body
    values = streams[0].get("values", [])
    assert values, "No log values in stream"

    # Loki returns [timestamp_ns, log_line] pairs
    log_line = values[0][1] if len(values[0]) > 1 else ""
    assert log_line, "Empty log line"

    # Extract JSON portion: find first '{' and last '}'
    json_start = log_line.find("{")
    json_end = log_line.rfind("}")
    if json_start == -1 or json_end == -1:
        pytest.fail(f"No JSON object found in log line:\n{log_line[:500]}")
    json_str = log_line[json_start : json_end + 1]

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"Log body is not valid JSON: {e}\n"
            f"Extracted JSON: {json_str[:500]}\n"
            f"Full line: {log_line[:500]}"
        )

    # Verify original keys are preserved
    assert "event" in parsed, "Log body missing 'event' key"
    assert parsed.get("event") == "contract_test", (
        f"Expected event='contract_test', got '{parsed.get('event')}'"
    )
    assert "contract" in parsed, "Log body missing 'contract' key"
    assert "message" in parsed, "Log body missing 'message' key"
    print(f"✅ Log body is valid JSON with keys: {list(parsed.keys())}")


# ── OBS-CONTRACT-004: Datasource Resolution ────────────────────────────


@when("an external plane queries Grafana API for datasources")
def query_grafana_datasources_for_contract(stack: ObservabilityStack) -> None:
    """Fetch Grafana datasource list for cross-plane validation."""
    grafana = stack.grafana()
    datasources = grafana.datasources()
    assert len(datasources) >= 4, f"Expected >= 4 datasources, got {len(datasources)}"
    pytest._step_context = {"contract_datasources": datasources}
    print(f"✅ Found {len(datasources)} datasources in Grafana")


@then(parsers.parse('the {datasource_name} datasource should use "{expected_url}"'))
def datasource_url_matches(
    stack: ObservabilityStack, datasource_name: str, expected_url: str
) -> None:
    """Assert a datasource's URL matches the expected value."""
    ctx = getattr(pytest, "_step_context", {})
    datasources = ctx.get("contract_datasources")
    assert datasources is not None, "No datasources in step context"

    found_ds = None
    for ds in datasources:
        if ds.get("name", "").lower().startswith(datasource_name.lower()):
            found_ds = ds
            break

    assert found_ds is not None, f"Datasource '{datasource_name}' not found in Grafana"

    actual_url = _normalize_datasource_url(found_ds.get("url", ""))
    expected_normalized = _normalize_datasource_url(expected_url)

    assert actual_url == expected_normalized, (
        f"Datasource '{datasource_name}' URL mismatch:\n"
        f"  Expected: {expected_url}\n"
        f"  Actual:   {found_ds.get('url')}"
    )
    print(f"✅ Datasource '{datasource_name}' URL matches: {expected_url}")
