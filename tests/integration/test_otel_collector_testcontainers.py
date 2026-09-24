"""
Testcontainers spike (#413) — migrates TestOTelCollectorHealth's assertions
from test_otel_collector.py to a self-provisioned, per-test-run stack instead
of assuming `make up` already ran against a shared instance.

Why this exists as a separate file rather than editing test_otel_collector.py
in place: this is the proof-of-approach for docs/TESTING_PYRAMID.md, not the
full migration (#416) — see that issue for migrating the rest of
tests/integration/ once this pattern is validated.

Run:  pytest tests/integration/test_otel_collector_testcontainers.py -v
      (no `make up` needed first — this provisions its own containers)
"""

from __future__ import annotations

import pathlib

import pytest
import requests
from testcontainers.compose import DockerCompose

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def otel_stack():
    """Provision otel-collector (+ its compose depends_on: prometheus,
    tempo, loki) for this test module only, torn down on exit regardless
    of test outcome — the isolation property the shared-stack pattern
    doesn't have."""
    with DockerCompose(
        context=str(REPO_ROOT),
        compose_file_name="compose.yaml",
        services=["otel-collector"],
        profiles=["core"],
        wait=True,  # DockerCompose's own readiness wait, not a fixed sleep
    ) as compose:
        yield compose


@pytest.fixture(scope="module")
def otel_metrics_url(otel_stack: DockerCompose) -> str:
    host, port = otel_stack.get_service_host_and_port("otel-collector", 8888)
    return f"http://{host}:{port}"


class TestOTelCollectorHealthTestcontainers:
    """Same assertions as TestOTelCollectorHealth in test_otel_collector.py,
    against a hermetic per-module stack instead of an externally-started
    shared one."""

    def test_otel_collector_is_running(self, otel_metrics_url: str) -> None:
        response = requests.get(f"{otel_metrics_url}/metrics", timeout=10)
        assert response.status_code == 200, "OTel Collector should return 200 OK"
        assert len(response.text) > 0, "OTel Collector should return metrics"
        assert "otelcol" in response.text, "Metrics should contain otelcol metrics"

    def test_otel_collector_uptime(self, otel_metrics_url: str) -> None:
        response = requests.get(f"{otel_metrics_url}/metrics", timeout=10)
        uptime_lines = [
            line
            for line in response.text.splitlines()
            if line.startswith("otelcol_process_uptime") and not line.startswith("#")
        ]
        assert len(uptime_lines) > 0, "Should report process uptime"
        uptime_value = float(uptime_lines[0].split()[-1])
        assert uptime_value > 0, "Uptime should be positive"
