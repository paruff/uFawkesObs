"""DORA event seeder for uFawkesObs acceptance tests.

Sends real deployment events over REST to dora-api's /event endpoint so
dora-compute has something to compute DORA metrics from. Replaces a
previous DORAWorkload class that sent OTLP trace spans instead -- the same
"OTLP instead of REST" mismatch found and fixed in uFawkesPipe's
notify-obs step (PR #70) -- and was never actually invoked by any
scenario (dead code; see OBS-SLI-006 investigation, 2026-08-18).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import requests
from pytest_bdd import given

from tests.acceptance.runtime import ObservabilityStack

# How long to wait (seconds) for dora_deployment_frequency_per_week to appear
# in Prometheus after seeding the event. Covers:
#   DORA_COMPUTE_INTERVAL_SECONDS (15 in CI) + Prometheus pushgateway
#   scrape_interval (15 s after PR #253 fix) + container-startup latency.
_DORA_PROPAGATION_TIMEOUT_S = 90


def build_deployment_event(
    repo: str = "paruff/uFawkesObs",
    service: str = "acceptance-test-plane",
    environment: str = "test",
    status: str = "success",
) -> dict[str, Any]:
    """Build a deployment event payload matching deployment-event.schema.json."""
    return {
        "schema_version": "1.0",
        "event_type": "deployment",
        "repo": repo,
        "service": service,
        "environment": environment,
        "commit_sha": uuid.uuid4().hex + uuid.uuid4().hex[:8],
        "deployed_at": datetime.now(UTC).isoformat(),
        "status": status,
        "pipeline_url": "https://github.com/paruff/uFawkesObs/actions/runs/0",
    }


def seed_deployment_event(
    dora_api_base_url: str = "http://localhost:8088", **overrides: Any
) -> dict[str, Any]:
    """POST a deployment event to dora-api and return the response body."""
    event = build_deployment_event(**overrides)
    resp = requests.post(
        f"{dora_api_base_url.rstrip('/')}/event", json=event, timeout=10
    )
    resp.raise_for_status()
    return resp.json()


@given("a DORA deployment event has been recorded")
def seeded_dora_deployment_event(stack: ObservabilityStack) -> None:
    """Seed one successful deployment event and wait for it to reach Prometheus.

    After posting the event to dora-api this step polls Prometheus until
    ``dora_deployment_frequency_per_week`` appears, ensuring the full
    dora-compute → Pushgateway → Prometheus scrape cycle has completed
    before OBS-SLI-006 queries the DORA Overview dashboard.

    Without this wait the dashboard check races against:
    - dora-compute's DORA_COMPUTE_INTERVAL_SECONDS cycle (15 s in CI)
    - Prometheus's pushgateway scrape_interval (15 s after the config fix)
    and shows 0/14 panels on a fresh boot even though the label queries
    are correct (the root cause of issue #253).
    """
    seed_deployment_event()

    promql = stack.promql()
    found, elapsed, _ = promql.poll_metric(
        "dora_deployment_frequency_per_week",
        timeout=_DORA_PROPAGATION_TIMEOUT_S,
        interval=5.0,
    )
    if found:
        print(
            f"✅ dora_deployment_frequency_per_week visible in Prometheus "
            f"after {elapsed:.1f}s"
        )
    else:
        raise AssertionError(
            f"dora_deployment_frequency_per_week not visible in Prometheus "
            f"after {_DORA_PROPAGATION_TIMEOUT_S}s — "
            f"dora-compute → Pushgateway → Prometheus pipeline did not complete. "
            f"Check dora-compute logs and the Pushgateway /metrics endpoint."
        )
