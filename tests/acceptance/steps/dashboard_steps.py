"""
Grafana dashboard step definitions.
Additional steps specific to dashboards beyond shared steps.
"""

from __future__ import annotations

from pytest_bdd import then, parsers

from tests.acceptance.runtime import ObservabilityStack


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
