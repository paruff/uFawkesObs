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
def seeded_dora_deployment_event() -> None:
    """Seed one successful deployment event via the real REST ingestion path.

    dora-compute runs its first compute cycle immediately on container
    start (see dora/compute/run.sh) and then on DORA_COMPUTE_INTERVAL_SECONDS
    -- CI sets that short so a cycle after this seed has a chance to pick
    the event up before OBS-SLI-006 queries Prometheus.
    """
    seed_deployment_event()
