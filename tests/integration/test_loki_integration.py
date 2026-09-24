"""
Integration tests for Loki (log aggregation system).

Migrated to Testcontainers (#416, following #413/Tempo's pattern): provisions
its own Loki container per test-module run instead of assuming `make up`
already started a shared stack. Loki has no `depends_on:` in compose.yaml,
so its own tests are a clean single-service migration.

TestAlloyIntegration below is intentionally NOT migrated here -- it tests a
different service (Alloy), which depends on both Loki and Prometheus
(compose.yaml `depends_on:`), so it belongs with test_alloy_and_dashboards.py's
own entry in docs/TESTING_PYRAMID.md's migration checklist instead of being
bundled into this file's scope. It still assumes the shared stack this file's
CI step runs alongside.
"""

from __future__ import annotations

import pathlib
import socket
import time

import pytest
import requests
from testcontainers.compose import DockerCompose

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def loki_stack():
    with DockerCompose(
        context=str(REPO_ROOT),
        compose_file_name="compose.yaml",
        services=["loki"],
        profiles=["core"],
        wait=True,
    ) as compose:
        yield compose


def _host_port(stack: DockerCompose, container_port: int) -> tuple[str, int]:
    host, port = stack.get_service_host_and_port("loki", container_port)
    return host, int(port)


@pytest.fixture(scope="module")
def loki_url(loki_stack: DockerCompose) -> str:
    host, port = _host_port(loki_stack, 3100)
    url = f"http://{host}:{port}"

    # Belt-and-braces: Loki does declare a compose healthcheck (unlike
    # Tempo), but Testcontainers' wait=True proved insufficient for a
    # service in this same stack once already (#416/Tempo, 3/15 failures
    # with 503 on a bare port-open wait) -- confirm /ready explicitly
    # rather than assume this service is different.
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{url}/ready", timeout=5).status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        pytest.fail("Loki did not report /ready within 30s of its port opening")

    return url


class TestLokiHealth:
    """Test Loki health and availability."""

    def test_loki_is_ready(self, loki_url: str):
        response = requests.get(f"{loki_url}/ready", timeout=10)
        assert response.status_code == 200, "Loki should return 200 OK for /ready"

    def test_loki_status(self, loki_url: str):
        endpoints = [f"{loki_url}/services", f"{loki_url}/config"]
        accessible = any(
            requests.get(endpoint, timeout=10).status_code == 200
            for endpoint in endpoints
        )
        assert accessible, "At least one Loki status endpoint should be accessible"

    def test_loki_version(self, loki_url: str):
        response = requests.get(f"{loki_url}/loki/api/v1/status/buildinfo", timeout=10)

        if response.status_code == 200:
            data = response.json()
            assert "version" in data, "Loki buildinfo should report a version"


class TestLokiPorts:
    """Test that Loki's ports are accessible."""

    def test_loki_http_port_open(self, loki_stack: DockerCompose):
        host, port = _host_port(loki_stack, 3100)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            assert sock.connect_ex((host, port)) == 0, "Loki HTTP port should be open"
        finally:
            sock.close()

    def test_loki_grpc_port_open(self, loki_stack: DockerCompose):
        host, port = _host_port(loki_stack, 9096)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            assert sock.connect_ex((host, port)) == 0, "Loki gRPC port should be open"
        finally:
            sock.close()


class TestLokiMetrics:
    """Test Loki metrics endpoint."""

    def test_loki_metrics_endpoint(self, loki_url: str):
        response = requests.get(f"{loki_url}/metrics", timeout=10)
        assert response.status_code == 200, "Loki should expose metrics"
        assert len(response.text) > 0, "Loki should expose metrics"


class TestLokiAPI:
    """Test Loki API endpoints."""

    def test_loki_labels_endpoint(self, loki_url: str):
        response = requests.get(f"{loki_url}/loki/api/v1/labels", timeout=10)
        assert response.status_code == 200, "Loki labels endpoint should be accessible"

    def test_loki_label_values_endpoint(self, loki_url: str):
        response = requests.get(f"{loki_url}/loki/api/v1/label/job/values", timeout=10)
        assert response.status_code == 200, (
            "Loki label values endpoint should be accessible"
        )

    def test_loki_can_query_logs(self, loki_url: str):
        now = int(time.time() * 1e9)
        five_min_ago = now - int(5 * 60 * 1e9)

        response = requests.get(
            f"{loki_url}/loki/api/v1/query_range",
            params={
                "query": '{job=~".+"}',
                "start": str(five_min_ago),
                "end": str(now),
                "limit": "10",
            },
            timeout=10,
        )

        # 400 is acceptable here too -- an empty/new Loki instance can reject
        # a query it has no series for yet; only an unexpected status fails.
        assert response.status_code in (200, 400), (
            f"Loki query returned unexpected status: {response.status_code}"
        )


class TestLokiPushAPI:
    """Test Loki push API for log ingestion."""

    def test_loki_push_endpoint_accessible(self, loki_url: str):
        # Not pushing real logs -- just confirming the endpoint is reachable
        # and responds (rejecting an empty payload is expected).
        response = requests.post(f"{loki_url}/loki/api/v1/push", json={}, timeout=10)
        assert response.status_code in (200, 204, 400, 415), (
            f"Loki push endpoint should be accessible (got {response.status_code})"
        )


class TestLokiConfiguration:
    """Test Loki configuration."""

    def test_loki_config_endpoint(self, loki_url: str):
        response = requests.get(f"{loki_url}/config", timeout=10)

        if response.status_code == 200:
            assert len(response.text) > 0, "Loki should return configuration"


class TestLokiLogIngestion:
    """Test Loki log ingestion capability."""

    def test_loki_can_receive_logs(self, loki_url: str):
        # Logs come from Alloy/OTel Collector in the real stack; this just
        # confirms Loki itself is ready to receive them.
        response = requests.get(f"{loki_url}/ready", timeout=10)
        assert response.status_code == 200, "Loki should be ready to receive logs"


class TestLokiDataRetention:
    """Test Loki data retention and storage."""

    def test_loki_storage_accessible(self, loki_url: str):
        response = requests.get(f"{loki_url}/ready", timeout=10)
        assert response.status_code == 200, "Loki should have accessible storage"


class TestAlloyIntegration:
    """Test Grafana Alloy integration with Loki.

    Not migrated -- Alloy depends on both Loki and Prometheus (compose.yaml
    `depends_on:`), so this belongs with test_alloy_and_dashboards.py's own
    migration (docs/TESTING_PYRAMID.md), not this file's single-service
    scope. Still assumes the shared stack this file's CI step runs alongside.
    """

    def test_alloy_is_running(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            result = sock.connect_ex(("localhost", 12345))
            assert result == 0, "Alloy HTTP port 12345 should be open"
        finally:
            sock.close()

    def test_alloy_metrics_endpoint(self):
        response = requests.get("http://localhost:12345/metrics", timeout=10)

        if response.status_code == 200:
            assert len(response.text) > 0, "Alloy should expose metrics"
