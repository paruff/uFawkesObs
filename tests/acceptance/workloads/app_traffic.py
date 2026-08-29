"""telemetry-generator traffic seeder for uFawkesObs acceptance tests.

Hits the real, already-documented telemetry-generator HTTP endpoints
(apps/telemetry-generator/README.md) so the app's OTel SDK metrics
(app_metrics_http_server_duration_milliseconds_*) have real samples for
OBS-SLI-006's dashboard checks -- previously nothing in this suite
generated HTTP traffic to the app at all, so Service - Error/Latency/SLO
dashboards had no data to show regardless of query correctness
(see issue #250).
"""

from __future__ import annotations

import requests
from pytest_bdd import given

TELEMETRY_GENERATOR_BASE_URL = "http://localhost:5001"


def generate_sample_traffic(base_url: str = TELEMETRY_GENERATOR_BASE_URL) -> None:
    """Hit /generate, /error, and /slow a few times each.

    Mirrors the "Generate load" example in apps/telemetry-generator/README.md.
    Best-effort: /error and /slow return non-2xx by design, and a single
    unreachable request shouldn't fail the whole seed step -- the dashboard
    assertion downstream is what actually judges success.
    """
    for _ in range(5):
        try:
            requests.get(f"{base_url}/generate", timeout=5)
        except requests.RequestException:
            pass
    for _ in range(2):
        try:
            requests.get(f"{base_url}/error", timeout=5)
        except requests.RequestException:
            pass
    try:
        requests.get(f"{base_url}/slow", timeout=10)
    except requests.RequestException:
        pass


@given("telemetry-generator has received sample HTTP traffic")
def seeded_app_traffic() -> None:
    """Generate a handful of real requests so app_metrics_http_server_*
    has samples by the time OBS-SLI-006 queries dashboards.

    OTEL_METRIC_EXPORT_INTERVAL is set short in CI (see
    .github/workflows/ci-acceptance-full.yml) so the OTel SDK's default
    60s export interval doesn't leave the metrics unexported within this
    scenario's window.
    """
    generate_sample_traffic()
