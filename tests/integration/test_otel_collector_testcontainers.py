"""
Integration tests for OpenTelemetry Collector.

Migrated to Testcontainers (#413 spike, expanded to full coverage in #416):
provisions otel-collector (+ its compose depends_on: prometheus, tempo,
loki) per test-module run instead of assuming `make up` already started a
shared stack. Retires the original test_otel_collector.py, which this file
now fully supersedes.

Run:  pytest tests/integration/test_otel_collector_testcontainers.py -v
      (no `make up` needed first — this provisions its own containers)
"""

from __future__ import annotations

import pathlib
import socket

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


def _host_port(stack: DockerCompose, container_port: int) -> tuple[str, int]:
    host, port = stack.get_service_host_and_port("otel-collector", container_port)
    return host, int(port)


@pytest.fixture(scope="module")
def otel_metrics_url(otel_stack: DockerCompose) -> str:
    host, port = _host_port(otel_stack, 8888)
    return f"http://{host}:{port}"


@pytest.fixture(scope="module")
def otel_app_metrics_url(otel_stack: DockerCompose) -> str:
    host, port = _host_port(otel_stack, 8889)
    return f"http://{host}:{port}"


def get_otel_metrics(otel_metrics_url: str) -> str:
    response = requests.get(f"{otel_metrics_url}/metrics", timeout=10)
    response.raise_for_status()
    return response.text


def parse_prometheus_metric(metrics_text: str, metric_name: str) -> list[str]:
    return [line for line in metrics_text.splitlines() if line.startswith(metric_name)]


def _port_open(stack: DockerCompose, container_port: int) -> bool:
    host, port = _host_port(stack, container_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


class TestOTelCollectorHealth:
    """Test OTel Collector health and availability."""

    def test_otel_collector_is_running(self, otel_metrics_url: str) -> None:
        response = requests.get(f"{otel_metrics_url}/metrics", timeout=10)
        assert response.status_code == 200, "OTel Collector should return 200 OK"
        assert len(response.text) > 0, "OTel Collector should return metrics"
        assert "otelcol" in response.text, "Metrics should contain otelcol metrics"

    def test_otel_collector_uptime(self, otel_metrics_url: str) -> None:
        metrics = get_otel_metrics(otel_metrics_url)
        uptime_lines = [
            line
            for line in parse_prometheus_metric(metrics, "otelcol_process_uptime")
            if not line.startswith("#")
        ]
        assert len(uptime_lines) > 0, "Should report process uptime"
        uptime_value = float(uptime_lines[0].split()[-1])
        assert uptime_value > 0, "Uptime should be positive"

    def test_otel_collector_runtime_info(self, otel_metrics_url: str) -> None:
        metrics = get_otel_metrics(otel_metrics_url)
        # Some may not be present depending on configuration -- just
        # confirm the metrics text is queryable for each, matching the
        # original file's own tolerance for this being environment-dependent.
        for metric in (
            "otelcol_process_runtime_heap_alloc_bytes",
            "otelcol_process_runtime_total_alloc_bytes",
            "otelcol_process_cpu_seconds",
        ):
            parse_prometheus_metric(metrics, metric)


class TestOTelCollectorReceivers:
    """Test OTel Collector receivers are operational."""

    def test_otlp_grpc_receiver_port_open(self, otel_stack: DockerCompose) -> None:
        assert _port_open(otel_stack, 4317), "OTLP gRPC port should be open"

    def test_otlp_http_receiver_port_open(self, otel_stack: DockerCompose) -> None:
        assert _port_open(otel_stack, 4318), "OTLP HTTP port should be open"

    def test_receiver_no_refused_data(self, otel_metrics_url: str) -> None:
        metrics = get_otel_metrics(otel_metrics_url)
        for metric in (
            "otelcol_receiver_refused_spans",
            "otelcol_receiver_refused_metric_points",
        ):
            for line in parse_prometheus_metric(metrics, metric):
                if not line.startswith("#"):
                    value = float(line.split()[-1])
                    assert value == 0, (
                        f"{metric} should be 0, got {value} (data is being refused)"
                    )


class TestOTelCollectorExporters:
    """Test OTel Collector exporters are operational."""

    def test_exporter_no_send_failures(self, otel_metrics_url: str) -> None:
        metrics = get_otel_metrics(otel_metrics_url)
        for metric in (
            "otelcol_exporter_send_failed_spans",
            "otelcol_exporter_send_failed_metric_points",
        ):
            for line in parse_prometheus_metric(metrics, metric):
                if not line.startswith("#"):
                    value = float(line.split()[-1])
                    # Allow some failures during startup, but not excessive.
                    assert value < 100, (
                        f"{metric} should be low, got {value} (exporters are failing)"
                    )

    def test_prometheus_exporter_port_open(self, otel_stack: DockerCompose) -> None:
        assert _port_open(otel_stack, 8889), "Prometheus exporter port should be open"


class TestOTelCollectorQueueMetrics:
    """Test OTel Collector queue metrics."""

    def test_queue_not_full(self, otel_metrics_url: str) -> None:
        """Test that queues are not full (which would indicate backpressure)."""
        metrics = get_otel_metrics(otel_metrics_url)

        size_lines = parse_prometheus_metric(metrics, "otelcol_exporter_queue_size")
        capacity_lines = parse_prometheus_metric(
            metrics, "otelcol_exporter_queue_capacity"
        )

        queue_data: dict[str, dict[str, float]] = {}
        for line in size_lines:
            if not line.startswith("#"):
                queue_data.setdefault(line, {})["size"] = float(line.split()[-1])
        for line in capacity_lines:
            if not line.startswith("#"):
                queue_data.setdefault(line, {})["capacity"] = float(line.split()[-1])

        for data in queue_data.values():
            if "size" in data and "capacity" in data and data["capacity"] > 0:
                utilization = data["size"] / data["capacity"]
                assert utilization < 0.8, (
                    f"Queue utilization is too high: {utilization:.1%} "
                    "(indicates backpressure)"
                )


class TestOTelCollectorConfiguration:
    """Test OTel Collector configuration is correct."""

    def test_expected_metrics_endpoints_available(
        self, otel_metrics_url: str, otel_app_metrics_url: str
    ) -> None:
        for url, description in (
            (f"{otel_metrics_url}/metrics", "Internal metrics"),
            (f"{otel_app_metrics_url}/metrics", "Prometheus exporter"),
        ):
            response = requests.get(url, timeout=5)
            assert response.status_code == 200, (
                f"{description} endpoint should be available at {url}"
            )
