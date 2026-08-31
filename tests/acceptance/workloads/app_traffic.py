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

from tests.acceptance.runtime import ObservabilityStack

TELEMETRY_GENERATOR_BASE_URL = "http://localhost:5001"

# How long to wait (seconds) for a rate()-based query over the freshly
# seeded traffic to become non-empty. Firing the requests below populates
# the raw counter, but Service - Error/Latency Analysis panels query
# rate()/increase() over a window -- PromQL needs at least 2 Prometheus
# scrapes of a rising counter before that returns any series at all, not
# just OTel SDK export completion. Without this wait, this step returned
# immediately after 8 requests and the dashboard check raced the same
# class of pipeline-propagation gap already fixed for DORA in #253 (see
# the poll_metric call in seeded_dora_deployment_event). Covers:
# OTEL_METRIC_EXPORT_INTERVAL (5s in CI) + 2x Prometheus scrape_interval
# (15s each) + container-startup latency.
_TRAFFIC_PROPAGATION_TIMEOUT_S = 90


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
def seeded_app_traffic(stack: ObservabilityStack) -> None:
    """Generate a handful of real requests, then wait for a rate() query
    over them to be non-empty before OBS-SLI-006 queries dashboards.

    OTEL_METRIC_EXPORT_INTERVAL is set short in CI (see
    .github/workflows/ci-acceptance-full.yml) so the OTel SDK's default
    60s export interval doesn't leave the metrics unexported within this
    scenario's window.
    """
    generate_sample_traffic()

    promql = stack.promql()
    found, elapsed, _ = promql.poll_metric(
        "rate(app_metrics_http_server_duration_milliseconds_count"
        '{job="telemetry-generator"}[5m])',
        timeout=_TRAFFIC_PROPAGATION_TIMEOUT_S,
        interval=5.0,
    )
    if found:
        print(f"✅ telemetry-generator traffic visible via rate() after {elapsed:.1f}s")
    else:
        raise AssertionError(
            f"app_metrics_http_server_duration_milliseconds_count rate() "
            f"still empty after {_TRAFFIC_PROPAGATION_TIMEOUT_S}s -- "
            f"telemetry-generator traffic never propagated through "
            f"OTel export + Prometheus scrape (see #274)"
        )
