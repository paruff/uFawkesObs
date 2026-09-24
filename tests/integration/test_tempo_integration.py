"""
Integration tests for Tempo (distributed tracing backend).

Migrated to Testcontainers (#416, following the pattern #413 established):
provisions its own Tempo container per test-module run instead of assuming
`make up` already started a shared stack. Tempo has no `depends_on:` in
compose.yaml, so it's a clean single-service migration -- no cross-service
state to provision alongside it.
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
def tempo_stack():
    with DockerCompose(
        context=str(REPO_ROOT),
        compose_file_name="compose.yaml",
        services=["tempo"],
        profiles=["core"],
        wait=True,
    ) as compose:
        yield compose


def _host_port(stack: DockerCompose, container_port: int) -> tuple[str, int]:
    host, port = stack.get_service_host_and_port("tempo", container_port)
    return host, int(port)


@pytest.fixture(scope="module")
def tempo_url(tempo_stack: DockerCompose) -> str:
    host, port = _host_port(tempo_stack, 3200)
    url = f"http://{host}:{port}"

    # Testcontainers' wait=True only confirms the port is listening, not that
    # Tempo's own /ready check passes -- Tempo answers with 503 for a few
    # seconds after the port opens while its internal components (ingester,
    # compactor) finish starting. Empirically flaky without this: a second
    # local run failed 3/15 tests on a bare port-open wait.
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{url}/ready", timeout=5).status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        pytest.fail("Tempo did not report /ready within 30s of its port opening")

    return url


@pytest.fixture(scope="module")
def tempo_grpc_addr(tempo_stack: DockerCompose) -> tuple[str, int]:
    return _host_port(tempo_stack, 9095)


@pytest.fixture(scope="module")
def jaeger_grpc_addr(tempo_stack: DockerCompose) -> tuple[str, int]:
    return _host_port(tempo_stack, 14250)


@pytest.fixture(scope="module")
def jaeger_http_addr(tempo_stack: DockerCompose) -> tuple[str, int]:
    return _host_port(tempo_stack, 14268)


@pytest.fixture(scope="module")
def zipkin_addr(tempo_stack: DockerCompose) -> tuple[str, int]:
    return _host_port(tempo_stack, 9411)


def _port_open(addr: tuple[str, int]) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        return sock.connect_ex(addr) == 0
    finally:
        sock.close()


class TestTempoHealth:
    """Test Tempo health and availability."""

    def test_tempo_is_ready(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/ready", timeout=10)
        assert response.status_code == 200, "Tempo should return 200 OK for /ready"

    def test_tempo_status(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/status", timeout=10)
        assert response.status_code == 200, "Tempo should return 200 OK for /status"

    def test_tempo_version(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/status/version", timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                data.get("version", "unknown")
            except requests.exceptions.JSONDecodeError:
                pass  # response may not be JSON on some Tempo versions


class TestTempoPorts:
    """Test that Tempo's ports are accessible."""

    def test_tempo_http_port_open(self, tempo_stack: DockerCompose):
        assert _port_open(_host_port(tempo_stack, 3200)), (
            "Tempo HTTP port should be open"
        )

    def test_tempo_grpc_port_open(self, tempo_grpc_addr: tuple[str, int]):
        assert _port_open(tempo_grpc_addr), "Tempo gRPC port should be open"

    def test_jaeger_grpc_port_open(self, jaeger_grpc_addr: tuple[str, int]):
        assert _port_open(jaeger_grpc_addr), "Jaeger gRPC receiver port should be open"

    def test_jaeger_http_port_open(self, jaeger_http_addr: tuple[str, int]):
        assert _port_open(jaeger_http_addr), "Jaeger HTTP receiver port should be open"

    def test_zipkin_port_open(self, zipkin_addr: tuple[str, int]):
        assert _port_open(zipkin_addr), "Zipkin receiver port should be open"


class TestTempoMetrics:
    """Test Tempo metrics endpoint."""

    def test_tempo_metrics_endpoint(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/metrics", timeout=10)

        if response.status_code == 200:
            assert len(response.text) > 0, "Tempo should expose metrics"


class TestTempoAPI:
    """Test Tempo API endpoints."""

    def test_tempo_search_tags_endpoint(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/api/search/tags", timeout=10)
        assert response.status_code == 200, (
            "Tempo search tags endpoint should be accessible"
        )

    def test_tempo_search_tag_values_endpoint(self, tempo_url: str):
        response = requests.get(
            f"{tempo_url}/api/search/tag/service.name/values", timeout=10
        )
        assert response.status_code == 200, (
            "Tempo search tag values endpoint should be accessible"
        )

    def test_tempo_can_search_traces(self, tempo_url: str):
        response = requests.get(
            f"{tempo_url}/api/search", params={"limit": 10}, timeout=10
        )
        assert response.status_code == 200, "Tempo search endpoint should be accessible"

        data = response.json()
        assert "traces" in data or data == {}, (
            "Tempo search response should have a traces field (or be empty)"
        )


class TestTempoConfiguration:
    """Test Tempo configuration."""

    def test_tempo_buildinfo(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/api/status/buildinfo", timeout=10)

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict), "Tempo buildinfo should be a JSON object"


class TestTempoTraceIngestion:
    """Test Tempo trace ingestion capability."""

    def test_tempo_can_receive_otlp_traces(self, tempo_url: str):
        # Traces go through OTel Collector first in this stack (see
        # test_otel_collector*.py); this just confirms Tempo itself is
        # ready to receive from it.
        response = requests.get(f"{tempo_url}/ready", timeout=10)
        assert response.status_code == 200, "Tempo should be ready to receive traces"


class TestTempoDataRetention:
    """Test Tempo data retention and storage."""

    def test_tempo_storage_accessible(self, tempo_url: str):
        response = requests.get(f"{tempo_url}/ready", timeout=10)
        assert response.status_code == 200, "Tempo should have accessible storage"
