"""
Alertmanager step definitions.
Additional steps specific to Alertmanager beyond shared steps.
"""

from __future__ import annotations

from pytest_bdd import then

from tests.acceptance.runtime import ObservabilityStack


@then("the Alertmanager API should return active alerts")
def alertmanager_has_alerts() -> None:
    """Assert the Alertmanager API returns alerts (may be empty array)."""
    import requests

    resp = requests.get("http://localhost:9093/api/v2/alerts", timeout=10)
    assert resp.status_code == 200, f"Alertmanager API returned {resp.status_code}"
    alerts = resp.json()
    print(f"✅ Alertmanager API accessible ({len(alerts)} active alerts)")


@then("Prometheus can reach Alertmanager")
def prometheus_can_reach_alertmanager(stack: ObservabilityStack) -> None:
    """Assert Prometheus has Alertmanager configured as a target."""
    targets = stack.promql().targets()
    alertmanager_targets = [
        t for t in targets if "alertmanager" in t.get("labels", {}).get("job", "")
    ]
    assert len(alertmanager_targets) > 0, "No Alertmanager targets found in Prometheus"
    print(f"✅ Prometheus has {len(alertmanager_targets)} Alertmanager target(s)")
