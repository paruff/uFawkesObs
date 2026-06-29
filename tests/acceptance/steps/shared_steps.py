"""
Shared step definitions used across multiple feature files.
Provides the "Given the core observability stack is running" step
and common assertion helpers.
"""

from __future__ import annotations

import time

import pytest
import requests
import yaml
from pathlib import Path
from pytest_bdd import given, then, when, parsers

from tests.acceptance.runtime import ObservabilityStack


# ── Given Steps ──────────────────────────────────────────────────────


@given("the core observability stack is running")
def core_stack_is_running(stack: ObservabilityStack) -> None:
    """Ensure the core stack is up and all services are healthy."""
    health = stack.wait_for_healthy()
    assert health.all_healthy, f"Stack not healthy:\n{health.summary()}"
    print(health.summary())


@given(parsers.parse('the YAML file "{file_path}" is loaded'))
def yaml_file_is_loaded(file_path: str, stack: ObservabilityStack) -> None:
    """Load a YAML file and store it in context for later steps."""
    path = Path(stack.compose_dir) / file_path
    assert path.exists(), f"YAML file '{file_path}' not found at {path}"
    content = yaml.safe_load(path.read_text())
    pytest._step_context = {"yaml_content": content, "yaml_path": file_path}
    print(f"✅ Loaded YAML: {file_path}")


@given("the stack has been running for at least 30 seconds")
def stack_running_30s() -> None:
    """Allow time for log ingestion and metric scraping to produce data."""
    time.sleep(30)


@given("synthetic telemetry is being generated")
def synthetic_telemetry_generated(stack: ObservabilityStack) -> None:
    """Start a synthetic workload that generates telemetry continuously."""
    from tests.acceptance.workloads import get_workload

    workload = get_workload("web_api", otlp_endpoint="http://localhost:4318")
    # Generate a few traces to ensure the pipeline is active
    for _ in range(3):
        workload.simulate_web_request()
    print("✅ Synthetic telemetry generated and sent to OTel Collector")


@given("the Grafana datasources are provisioned")
def grafana_datasources_provisioned(stack: ObservabilityStack) -> None:
    """Verify that Grafana has all expected datasources provisioned."""
    grafana = stack.grafana()

    expected_datasources = ["Prometheus", "Loki", "Tempo", "Alertmanager"]
    for ds_name in expected_datasources:
        ds = grafana.get_datasource_by_name(ds_name)
        assert ds is not None, f"Expected datasource '{ds_name}' not found in Grafana"
        assert ds.get("type") != "", f"Datasource '{ds_name}' has no type"
        print(f"✅ Datasource '{ds_name}' provisioned")

    print(f"✅ All {len(expected_datasources)} Grafana datasources are provisioned")


@given(parsers.parse('the "{datasource}" datasource is configured in Grafana'))
def datasource_configured(stack: ObservabilityStack, datasource: str) -> None:
    """Verify a specific datasource exists in Grafana."""
    grafana = stack.grafana()
    ds = grafana.get_datasource_by_name(datasource)
    assert ds is not None, f"Datasource '{datasource}' not found in Grafana"
    assert ds.get("type") != "", f"Datasource '{datasource}' has no type"
    print(
        f"✅ Datasource '{datasource}' found: type={ds.get('type')}, url={ds.get('url')}"
    )


# ── When Steps ────────────────────────────────────────────────────────


@when("I check the Grafana health endpoint")
def check_grafana_health(stack: ObservabilityStack) -> None:
    """Check Grafana health — result stored in step context."""
    healthy = stack.grafana().is_healthy()
    pytest._step_context = {"result": healthy}


@when(parsers.parse("I query Prometheus for '{query}'"))
def query_prometheus(stack: ObservabilityStack, query: str) -> None:
    """Execute a PromQL query and store the result."""
    promql = stack.promql()
    data = promql.query(query)
    pytest._step_context = {"query_result": data, "query": query}


@when(parsers.parse('I query Grafana for "{metric}" via the Prometheus datasource'))
def query_grafana_metric(stack: ObservabilityStack, metric: str) -> None:
    """Query a metric through Grafana's Prometheus datasource."""
    grafana = stack.grafana()
    result = grafana.ds_query("prometheus", metric)
    pytest._step_context = {"grafana_result": result, "metric": metric}


@when("I check the OTel Collector metrics endpoint")
def check_otel_metrics() -> None:
    """Check OTel Collector /metrics endpoint."""
    resp = requests.get("http://localhost:8888/metrics", timeout=10)
    pytest._step_context = {
        "otel_status_code": resp.status_code,
        "otel_metrics_text": resp.text,
    }


@when("I check the Loki ready endpoint")
def check_loki_ready() -> None:
    """Check Loki /ready endpoint."""
    resp = requests.get("http://localhost:3100/ready", timeout=10)
    pytest._step_context = {
        "status_code": resp.status_code,
        "loki_ready_code": resp.status_code,
    }


@when(parsers.parse("I query Loki for '{query}'"))
def query_loki(stack: ObservabilityStack, query: str) -> None:
    """Execute a LogQL query against Loki."""
    loki = stack.loki()
    result = loki.query_range(query)
    pytest._step_context = {"loki_result": result, "loki_query": query}


@when("I check the Alertmanager health endpoint")
def check_alertmanager_health() -> None:
    """Check Alertmanager health and config status."""
    resp = requests.get("http://localhost:9093/-/healthy", timeout=10)
    config_resp = requests.get("http://localhost:9093/metrics", timeout=10)
    config_ok = "alertmanager_config_last_reload_successful 1" in config_resp.text
    pytest._step_context = {
        "status_code": resp.status_code,
        "alertmanager_healthy_code": resp.status_code,
        "alertmanager_config_ok": config_ok,
    }


@when("I query Prometheus for alert rules")
def query_prometheus_rules(stack: ObservabilityStack) -> None:
    """Query Prometheus for alerting rules."""
    promql = stack.promql()
    rules = promql.rules()
    pytest._step_context = {"rules_result": rules}


@when("I fetch the Grafana datasource list")
def fetch_grafana_datasources(stack: ObservabilityStack) -> None:
    """Fetch all Grafana datasources."""
    grafana = stack.grafana()
    datasources = grafana.datasources()
    pytest._step_context = {"datasources": datasources}


@when("I fetch the Grafana dashboard list")
def fetch_grafana_dashboards(stack: ObservabilityStack) -> None:
    """Fetch all Grafana dashboards."""
    grafana = stack.grafana()
    dashboards = grafana.dashboards()
    pytest._step_context = {"dashboards": dashboards}


# ── Then Steps ────────────────────────────────────────────────────────


@then(parsers.parse("the endpoint should return HTTP {status_code:d}"))
def endpoint_returns_status(status_code: int) -> None:
    """Assert an HTTP status code from a previous when-step."""
    ctx = getattr(pytest, "_step_context", {})
    # Check various possible keys for HTTP status
    for key, value in ctx.items():
        if "status_code" in key or "status" in key:
            assert value == status_code, (
                f"Expected HTTP {status_code}, got {value} (key={key})"
            )
            return
    pytest.fail(f"No HTTP status code found in step context: {ctx}")


@then(parsers.parse("it should return HTTP {status_code:d}"))
def it_returns_status(status_code: int) -> None:
    """Alias for endpoint_returns_status."""
    endpoint_returns_status(status_code)


@then(parsers.parse('the response should contain "{text}"'))
def response_contains(text: str) -> None:
    """Assert the response text contains expected content."""
    ctx = getattr(pytest, "_step_context", {})
    for key, value in ctx.items():
        if isinstance(value, str) and text in value:
            return
        if isinstance(value, (list, dict)) and text in str(value):
            return
    pytest.fail(f"Expected '{text}' not found in step context: {list(ctx.keys())}")


@then(parsers.parse('the result should have value "{expected}"'))
def result_has_value(expected: str) -> None:
    """Assert a PromQL query result has a specific value."""
    ctx = getattr(pytest, "_step_context", {})
    data = ctx.get("query_result")
    assert data is not None, "No query result in step context"
    results = data.get("result", [])
    assert len(results) > 0, "No results returned from PromQL query"
    value = results[0].get("value", [0, "0"])[1]
    assert value == expected, f"Expected value '{expected}', got '{value}'"


@then("the scrape duration should be under 1 second")
def scrape_duration_under_1s(stack: ObservabilityStack) -> None:
    """Assert the OTel Collector scrape duration is under 1 second."""
    ctx = getattr(pytest, "_step_context", {})
    query = ctx.get("query", "")
    if "otel-collector" not in query:
        # Re-query for scrape duration specifically
        pass
    promql = stack.promql()
    data = promql.query('scrape_duration_seconds{job="otel-collector"}')
    results = data.get("result", [])
    assert len(results) > 0, "No scrape duration data found"
    duration = float(results[0].get("value", [0, "0"])[1])
    assert duration < 1.0, f"Scrape duration {duration}s exceeds 1s SLA"


@then("the response should contain at least 1 data point")
def response_has_data_point() -> None:
    """Assert a Grafana query response has at least 1 data point."""
    ctx = getattr(pytest, "_step_context", {})
    result = ctx.get("grafana_result")
    assert result is not None, "No Grafana result in step context"
    frames = result.get("results", {}).get("A", {}).get("frames", [])
    assert len(frames) > 0, "No frames in Grafana response"
    values = frames[0].get("data", {}).get("values", [])
    assert len(values) > 1, "No value data in Grafana response"
    data_points = values[1] if values else []
    assert len(data_points) >= 1, f"Expected >=1 data points, got {len(data_points)}"


@then("the data point value should be positive")
def data_point_positive() -> None:
    """Assert the first data point value is positive."""
    ctx = getattr(pytest, "_step_context", {})
    result = ctx.get("grafana_result")
    assert result is not None, "No Grafana result in step context"
    frames = result.get("results", {}).get("A", {}).get("frames", [])
    assert len(frames) > 0, "No frames in Grafana response"
    values = frames[0].get("data", {}).get("values", [])
    assert len(values) > 1 and len(values[1]) > 0, "No data point values"
    first_value = values[1][0]
    assert first_value is not None and first_value > 0, (
        f"Expected positive value, got {first_value}"
    )


@then("at least 1 log stream should be returned")
def at_least_one_log_stream() -> None:
    """Assert Loki query returned at least 1 log stream."""
    ctx = getattr(pytest, "_step_context", {})
    result = ctx.get("loki_result")
    assert result is not None, "No Loki result in step context"
    streams = result.get("data", {}).get("result", [])
    assert len(streams) >= 1, f"Expected >=1 log stream, got {len(streams)}"
    print(f"✅ Found {len(streams)} log streams")


@then(parsers.parse("the query should return results within {timeout:d} seconds"))
def query_returns_within(stack: ObservabilityStack, timeout: int) -> None:
    """Assert a LogQL query returns results within a timeout."""
    ctx = getattr(pytest, "_step_context", {})
    query = ctx.get("loki_query")
    assert query is not None, "No Loki query in step context"
    loki = stack.loki()
    start = time.time()
    while time.time() - start < timeout:
        result = loki.query_range(query)
        streams = result.get("data", {}).get("result", [])
        if len(streams) > 0:
            elapsed = time.time() - start
            print(f"✅ Log streams found after {elapsed:.1f}s")
            return
        time.sleep(2)
    pytest.fail(f"No results for '{query}' within {timeout}s")


@then("the configuration should be loaded successfully")
def alertmanager_config_loaded() -> None:
    """Assert Alertmanager configuration loaded successfully."""
    ctx = getattr(pytest, "_step_context", {})
    assert ctx.get("alertmanager_config_ok"), (
        "Alertmanager config reload not successful"
    )


@then(parsers.parse("at least {count:d} alerting rule should be present"))
def at_least_alert_rules(count: int) -> None:
    """Assert at least N alerting rules exist in Prometheus."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result")
    assert rules_data is not None, "No rules result in step context"
    groups = rules_data.get("groups", [])
    total_rules = sum(len(g.get("rules", [])) for g in groups)
    assert total_rules >= count, (
        f"Expected >= {count} alerting rules, found {total_rules}"
    )


@then(parsers.parse('the rules should have a "{group_name}" group'))
def rules_have_group(group_name: str) -> None:
    """Assert alert rules include a specific group name."""
    ctx = getattr(pytest, "_step_context", {})
    rules_data = ctx.get("rules_result")
    assert rules_data is not None, "No rules result in step context"
    groups = [g.get("name") for g in rules_data.get("groups", [])]
    assert group_name in groups, f"Expected group '{group_name}' not found in: {groups}"


@then(parsers.parse('the list should contain a "{name}" datasource'))
def datasource_in_list(name: str) -> None:
    """Assert a datasource exists in the Grafana datasource list."""
    ctx = getattr(pytest, "_step_context", {})
    datasources = ctx.get("datasources")
    assert datasources is not None, "No datasources in step context"
    found = any(ds.get("name") == name for ds in datasources)
    assert found, f"Datasource '{name}' not found in Grafana datasources"
    print(f"✅ Datasource '{name}' found")


@then(parsers.parse('the list should contain a dashboard with UID "{uid}"'))
def dashboard_uid_in_list(uid: str) -> None:
    """Assert a dashboard with a specific UID exists."""
    ctx = getattr(pytest, "_step_context", {})
    dashboards = ctx.get("dashboards")
    assert dashboards is not None, "No dashboards in step context"
    found = any(d.get("uid") == uid for d in dashboards)
    assert found, f"Dashboard with UID '{uid}' not found in Grafana"
    print(f"✅ Dashboard '{uid}' found")
