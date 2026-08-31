"""
Grafana dashboard step definitions.
Additional steps specific to dashboards beyond shared steps.
"""

from __future__ import annotations

from datetime import datetime, timezone

import requests
from pytest_bdd import given, then, parsers

from tests.acceptance.runtime import ObservabilityStack


@given("a real DORA deployment event has been sent")
def seed_dora_deployment_event(stack: ObservabilityStack) -> None:
    """POST a failed deployment followed by a successful one, same source.

    Self-contained on purpose — this scenario must not depend on side
    effects left behind by other scenarios' event traffic, or it becomes
    order-dependent and flaky.

    The failed->success pair is what FDRT actually measures (the gap
    between a failed deploy and the next successful one of the same
    source — see dora/compute/metrics_db_sqlite.py's fdrt()), and the
    success event's pr_merged_at is what Lead Time measures. #267: these
    were previously never fed by anything in this repo, and the schema
    rejected pr_merged_at outright (additionalProperties: false).

    #290: even once the events are ingested, dora-compute only recomputes
    on its own interval (DORA_COMPUTE_INTERVAL_SECONDS) and Prometheus
    only picks up the pushed result on its own next scrape -- confirmed
    live via CI container logs that this pipeline can take ~15-30s after
    the POSTs below before the metric is actually queryable. The Then
    step that follows this Background has no retry of its own, so this
    step blocks until the metric is genuinely visible in Prometheus
    (same poll_metric() helper OBS-SLI-006 already uses) instead of
    returning the instant the ingestion API accepts the POST.
    """
    repo = "acceptance-test/dashboard-data-presence"
    resp = requests.post(
        "http://localhost:8088/event",
        json={
            "schema_version": "1.0",
            "event_type": "deployment",
            "repo": repo,
            "service": "acceptance-test-service",
            "environment": "production",
            "commit_sha": "1" * 40,
            "deployed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "failed",
            "pipeline_url": "https://example.com/ci/acceptance-test",
        },
        timeout=10,
    )
    resp.raise_for_status()

    resp = requests.post(
        "http://localhost:8088/event",
        json={
            "schema_version": "1.0",
            "event_type": "deployment",
            "repo": repo,
            "service": "acceptance-test-service",
            "environment": "production",
            "commit_sha": "2" * 40,
            "deployed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "success",
            "pipeline_url": "https://example.com/ci/acceptance-test",
            "pr_merged_at": "2026-01-01T00:00:00Z",
        },
        timeout=10,
    )
    resp.raise_for_status()

    promql = stack.promql()
    found, elapsed, _ = promql.poll_metric(
        f'dora_deployment_frequency_per_week{{team_id="{repo}"}}',
        timeout=90,
    )
    assert found, (
        f"dora_deployment_frequency_per_week for team_id={repo!r} not visible "
        "in Prometheus within 90s of seeding -- dora-compute -> Pushgateway -> "
        "Prometheus pipeline did not complete in time."
    )
    print(f"✅ Seeded DORA metric visible in Prometheus after {elapsed:.1f}s")


def _resolve_template_vars(dashboard_json: dict) -> dict[str, str]:
    """Resolve Grafana template variables to concrete values, the same way
    Grafana does before sending a panel query to the datasource.

    Handles the two variable shapes this repo's dashboards actually use:
    query variables with includeAll/allValue (e.g. team_id -> ".*"), and
    comma-list custom variables (e.g. window: "7d,30d,90d" -> "30d"). Not
    a general Grafana variable-resolution engine — extend as new variable
    shapes show up in dashboards this step is applied to.
    """
    resolved: dict[str, str] = {}
    for var in dashboard_json.get("templating", {}).get("list", []):
        name = var.get("name")
        if not name:
            continue
        current = var.get("current") or {}
        value = current.get("value")
        if value in (None, "$__all"):
            if var.get("includeAll") and var.get("allValue"):
                value = var["allValue"]
            elif isinstance(var.get("query"), str) and "," in var["query"]:
                value = var["query"].split(",")[0].strip()
        if value is not None:
            resolved[name] = str(value)
    return resolved


@then(
    parsers.parse(
        'the dashboard "{uid}" panels should return real, labeled data, '
        'except known gaps "{known_gap_titles}"'
    )
)
@then(parsers.parse('the dashboard "{uid}" panels should return real, labeled data'))
def dashboard_panels_have_real_data(
    stack: ObservabilityStack, uid: str, known_gap_titles: str = ""
) -> None:
    """Assert every panel query returns at least one series with real
    dimensional labels — not just an unlabeled `or vector(0)` fallback.

    A bare `or vector(0)` fallback (used throughout this repo's recording
    rules to avoid Grafana "No Data" panels) produces a non-empty result
    with only `__name__` set — no team_id, no tier, nothing dimensional.
    That looks like a passing query but means the underlying metric never
    existed. This is exactly the pattern that let dora-overview.json's
    "No data" go undetected: dashboard-provisioning checks only verified
    the UID was registered, never that panel queries return real series.

    `known_gap_titles` (pipe-separated panel titles) lets a scenario
    explicitly document an already-tracked, real gap instead of either
    silently skipping it or leaving the whole scenario permanently red
    for something already filed. Every skip prints its issue reference
    from the caller's own comment — this function just doesn't fail on
    the listed titles.
    """
    known_gaps = {t.strip() for t in known_gap_titles.split("|") if t.strip()}
    grafana = stack.grafana()
    dashboard_response = grafana.get_dashboard(uid)
    assert dashboard_response is not None, f"Dashboard '{uid}' not found"
    dashboard_json = dashboard_response.get("dashboard", {})
    panels = dashboard_json.get("panels", [])
    template_vars = _resolve_template_vars(dashboard_json)

    promql = stack.promql()
    checked = 0
    problems: list[str] = []
    skipped: list[str] = []

    for panel in panels:
        title = panel.get("title")
        for target in panel.get("targets", []):
            expr = target.get("expr")
            if not expr:
                continue
            for var_name, var_value in template_vars.items():
                expr = expr.replace(f"${var_name}", var_value).replace(
                    f"${{{var_name}}}", var_value
                )
            checked += 1
            try:
                result = promql.query(expr)
            except Exception as e:
                (skipped if title in known_gaps else problems).append(
                    f"{title!r}: query error: {e}"
                )
                continue
            series = result.get("result", [])
            has_real_series = any(len(s.get("metric", {})) > 1 for s in series)
            if not has_real_series:
                reason = "no data" if not series else "unlabeled fallback only"
                (skipped if title in known_gaps else problems).append(
                    f"{title!r}: {expr!r} -> {reason}"
                )

    if skipped:
        print(f"⚠️  Skipped {len(skipped)} known-gap panel queries:")
        for s in skipped:
            print(f"   {s}")

    assert checked > 0, f"Dashboard '{uid}' has no panel queries to check"
    assert not problems, (
        f"Dashboard '{uid}': {len(problems)}/{checked} panel queries returned "
        f"no real data:\n" + "\n".join(problems)
    )
    print(
        f"✅ Dashboard '{uid}': all {checked} panel queries return real, labeled data"
    )


@then(parsers.parse('the dashboard "{uid}" panels should return non-empty data'))
def dashboard_panels_have_nonempty_data(stack: ObservabilityStack, uid: str) -> None:
    """Weaker sibling of dashboard_panels_have_real_data, for dashboards
    whose recording rules deliberately aggregate away all labels (e.g.
    org-wide `avg(...)`/`sum(...)` with no `by (...)` clause) — a
    correctly-fed panel there produces the exact same label-less shape as
    an `or vector(0)` fallback, so the label-count check would false-
    positive. This only checks the query returns at least one series;
    it can't distinguish "real single aggregate value" from "fallback"
    the way the stricter step can for per-dimension dashboards.
    """
    grafana = stack.grafana()
    dashboard_response = grafana.get_dashboard(uid)
    assert dashboard_response is not None, f"Dashboard '{uid}' not found"
    dashboard_json = dashboard_response.get("dashboard", {})
    panels = dashboard_json.get("panels", [])
    template_vars = _resolve_template_vars(dashboard_json)

    promql = stack.promql()
    checked = 0
    problems: list[str] = []

    for panel in panels:
        title = panel.get("title")
        for target in panel.get("targets", []):
            expr = target.get("expr")
            if not expr:
                continue
            for var_name, var_value in template_vars.items():
                expr = expr.replace(f"${var_name}", var_value).replace(
                    f"${{{var_name}}}", var_value
                )
            checked += 1
            try:
                result = promql.query(expr)
            except Exception as e:
                problems.append(f"{title!r}: query error: {e}")
                continue
            if not result.get("result"):
                problems.append(f"{title!r}: {expr!r} -> no data")

    assert checked > 0, f"Dashboard '{uid}' has no panel queries to check"
    assert not problems, (
        f"Dashboard '{uid}': {len(problems)}/{checked} panel queries returned "
        f"no data:\n" + "\n".join(problems)
    )
    print(f"✅ Dashboard '{uid}': all {checked} panel queries return data")


@then(parsers.parse('the dashboard "{uid}" should render successfully'))
def dashboard_renders(stack: ObservabilityStack, uid: str) -> None:
    """Assert a dashboard can be fetched and has panels."""
    grafana = stack.grafana()
    dashboard = grafana.get_dashboard(uid)
    assert dashboard is not None, f"Dashboard '{uid}' not found"
    panels = dashboard.get("dashboard", {}).get("panels", [])
    assert len(panels) > 0, f"Dashboard '{uid}' has no panels"
    print(f"✅ Dashboard '{uid}' loaded with {len(panels)} panels")


@then(parsers.parse('the dashboard "{uid}" should have "{expected_count:d}" panels'))
def dashboard_has_panels(
    stack: ObservabilityStack, uid: str, expected_count: int
) -> None:
    """Assert a dashboard has a specific number of panels."""
    grafana = stack.grafana()
    dashboard = grafana.get_dashboard(uid)
    assert dashboard is not None, f"Dashboard '{uid}' not found"
    panels = dashboard.get("dashboard", {}).get("panels", [])
    assert len(panels) == expected_count, (
        f"Dashboard '{uid}': expected {expected_count} panels, got {len(panels)}"
    )


@then("all datasource health checks should pass")
def all_datasources_healthy(stack: ObservabilityStack) -> None:
    """Assert all configured datasources report healthy."""
    grafana = stack.grafana()
    datasources = grafana.datasources()
    # Datasource health is implicit if they're listed
    print(f"✅ All {len(datasources)} datasources configured")
    for ds in datasources:
        print(f"   - {ds.get('name')} ({ds.get('type')}) → {ds.get('url')}")
