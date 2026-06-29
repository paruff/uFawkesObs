"""
ObservabilityStack — unified runtime for uFawkesObs acceptance tests.

Provides Docker Compose lifecycle management, typed API clients for each
observability service, synthetic workload generation, and evidence capture.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Tuple

import requests

# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────

DEFAULT_COMPOSE_DIR = Path(__file__).resolve().parents[2]  # repo root

SERVICE_PORTS: dict[str, dict[str, int]] = {
    "otel-collector": {
        "otlp-grpc": 4317,
        "otlp-http": 4318,
        "self-metrics": 8888,
        "prometheus-exporter": 8889,
    },
    "prometheus": {"http": 9090},
    "alertmanager": {"http": 9093},
    "tempo": {"http": 3200, "grpc": 9095},
    "loki": {"http": 3100, "grpc": 9096},
    "alloy": {"http": 12345},
    "grafana": {"http": 3000},
    "node-exporter": {"http": 9100},
}

SERVICE_HEALTH_URLS: dict[str, str] = {
    "prometheus": "http://localhost:9090/-/healthy",
    "alertmanager": "http://localhost:9093/-/healthy",
    "loki": "http://localhost:3100/ready",
    "alloy": "http://localhost:12345/-/ready",
    "grafana": "http://localhost:3000/api/health",
    "otel-collector": "http://localhost:8888/metrics",
}

HEALTH_CHECK_TIMEOUT = 120  # seconds
HEALTH_CHECK_INTERVAL = 2  # seconds

GRAFANA_DATASOURCE_UIDS = {
    "prometheus": "prometheus",
    "loki": "loki",
    "tempo": "tempo",
    "alertmanager": "alertmanager",
}


# ──────────────────────────────────────────────────────────────────────
# Data types
# ──────────────────────────────────────────────────────────────────────


@dataclass
class ServiceHealth:
    """Health status of a single service."""

    name: str
    healthy: bool
    elapsed: float
    status_code: int = 0
    error: str = ""


@dataclass
class StackHealth:
    """Aggregated health status of the entire stack."""

    all_healthy: bool
    services: list[ServiceHealth] = field(default_factory=list)
    elapsed: float = 0.0

    def summary(self) -> str:
        lines = [f"Stack health check ({self.elapsed:.1f}s):"]
        for s in self.services:
            icon = "✅" if s.healthy else "❌"
            lines.append(f"  {icon} {s.name} (HTTP {s.status_code})")
        return "\n".join(lines)


@dataclass
class Evidence:
    """Captured evidence from a test execution."""

    test_id: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    artifacts: dict[str, Any] = field(default_factory=dict)

    def add(self, key: str, value: Any) -> None:
        self.artifacts[key] = value

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.test_id}.json"
        path.write_text(
            json.dumps(
                {
                    "test_id": self.test_id,
                    "timestamp": self.timestamp,
                    "artifacts": self.artifacts,
                },
                indent=2,
                default=str,
            )
        )
        return path


# ──────────────────────────────────────────────────────────────────────
# API Clients
# ──────────────────────────────────────────────────────────────────────


class PromQLClient:
    """Client for Prometheus HTTP API v1."""

    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url.rstrip("/")

    def query(self, query: str, timeout: int = 10) -> dict[str, Any]:
        """Execute an instant PromQL query."""
        resp = requests.get(
            f"{self.base_url}/api/v1/query",
            params={"query": query},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "success":
            raise ValueError(f"PromQL query failed: {data.get('error', 'unknown')}")
        return data["data"]

    def query_range(
        self, query: str, start: float, end: float, step: int = 15, timeout: int = 10
    ) -> dict[str, Any]:
        """Execute a range PromQL query."""
        resp = requests.get(
            f"{self.base_url}/api/v1/query_range",
            params={"query": query, "start": start, "end": end, "step": step},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "success":
            raise ValueError(
                f"PromQL range query failed: {data.get('error', 'unknown')}"
            )
        return data["data"]

    def targets(self) -> list[dict[str, Any]]:
        """Get all active scrape targets."""
        resp = requests.get(f"{self.base_url}/api/v1/targets", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("activeTargets", [])

    def rules(self) -> dict[str, Any]:
        """Get all loaded rules."""
        resp = requests.get(f"{self.base_url}/api/v1/rules", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {})

    def is_healthy(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/-/healthy", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def is_ready(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/-/ready", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def get_metric(self, metric_name: str) -> list[dict[str, Any]]:
        """Query a metric name and return its result list."""
        data = self.query(metric_name)
        return data.get("result", [])

    def poll_metric(
        self,
        query: str,
        expected_value: Optional[float] = None,
        timeout: int = 60,
        interval: float = 2.0,
    ) -> Tuple[bool, float, Optional[dict]]:
        """Poll Prometheus until a metric appears or timeout.

        Returns:
            (found, elapsed_seconds, metric_data_or_None)
        """
        start = time.time()
        while time.time() - start < timeout:
            try:
                data = self.query(query)
                results = data.get("result", [])
                if results:
                    value = float(results[0]["value"][1])
                    if expected_value is None or value == expected_value:
                        return True, time.time() - start, results[0]
            except (requests.RequestException, ValueError, KeyError):
                pass
            time.sleep(interval)
        return False, time.time() - start, None


class LokiClient:
    """Client for Loki HTTP API."""

    def __init__(self, base_url: str = "http://localhost:3100"):
        self.base_url = base_url.rstrip("/")

    def query_range(
        self,
        query: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 100,
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Query Loki for log lines in a time range."""
        import datetime as dt

        if start is None:
            start_ns = int(
                (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5)).timestamp()
                * 1e9
            )
        else:
            start_ns = start
        if end is None:
            end_ns = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1e9)
        else:
            end_ns = end

        params = {
            "query": query,
            "start": str(start_ns),
            "end": str(end_ns),
            "limit": str(limit),
        }
        resp = requests.get(
            f"{self.base_url}/loki/api/v1/query_range",
            params=params,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def labels(self, timeout: int = 10) -> list[str]:
        """Get all label names."""
        resp = requests.get(f"{self.base_url}/loki/api/v1/labels", timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("data", [])

    def label_values(self, label: str, timeout: int = 10) -> list[str]:
        """Get all values for a label."""
        resp = requests.get(
            f"{self.base_url}/loki/api/v1/label/{label}/values",
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def is_ready(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/ready", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def stream_count(self, query: str = '{job="docker"}', timeout: int = 10) -> int:
        """Count log streams matching a query."""
        result = self.query_range(query, limit=1, timeout=timeout)
        return len(result.get("data", {}).get("result", []))

    def poll_logs(
        self,
        query: str = '{job="docker"}',
        min_streams: int = 1,
        timeout: int = 60,
        interval: float = 3.0,
    ) -> Tuple[bool, float, int]:
        """Poll Loki until log streams appear.

        Returns:
            (found, elapsed_seconds, stream_count)
        """
        start = time.time()
        while time.time() - start < timeout:
            count = self.stream_count(query)
            if count >= min_streams:
                return True, time.time() - start, count
            time.sleep(interval)
        return False, time.time() - start, self.stream_count(query)


class TempoClient:
    """Client for Tempo HTTP API."""

    def __init__(self, base_url: str = "http://localhost:3200"):
        self.base_url = base_url.rstrip("/")

    def is_ready(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/ready", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def query_trace(self, trace_id: str, timeout: int = 10) -> Optional[dict[str, Any]]:
        """Query a trace by ID."""
        try:
            resp = requests.get(
                f"{self.base_url}/api/traces/{trace_id}",
                timeout=timeout,
            )
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

    def search(self, query: str, limit: int = 20, timeout: int = 10) -> dict[str, Any]:
        """Search traces using TraceQL."""
        params = {"q": query, "limit": str(limit)}
        resp = requests.get(
            f"{self.base_url}/api/search",
            params=params,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def poll_trace(
        self,
        trace_id: str,
        timeout: int = 30,
        interval: float = 2.0,
    ) -> Tuple[bool, float, Optional[dict]]:
        """Poll Tempo until a trace is found.

        Returns:
            (found, elapsed_seconds, trace_data_or_None)
        """
        start = time.time()
        while time.time() - start < timeout:
            result = self.query_trace(trace_id)
            if result is not None:
                return True, time.time() - start, result
            time.sleep(interval)
        return False, time.time() - start, None


class GrafanaClient:
    """Client for Grafana HTTP API."""

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        username: str = "admin",
        password: str = "admin",
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password)

    def is_healthy(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def datasources(self) -> list[dict[str, Any]]:
        """Get all configured datasources."""
        resp = requests.get(
            f"{self.base_url}/api/datasources",
            auth=self.auth,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_datasource_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """Get a datasource by name."""
        for ds in self.datasources():
            if ds.get("name") == name:
                return ds
        return None

    def dashboards(self) -> list[dict[str, Any]]:
        """Get all dashboards."""
        resp = requests.get(
            f"{self.base_url}/api/search?type=dash-db",
            auth=self.auth,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_dashboard(self, uid: str) -> Optional[dict[str, Any]]:
        """Get a dashboard by UID."""
        try:
            resp = requests.get(
                f"{self.base_url}/api/dashboards/uid/{uid}",
                auth=self.auth,
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

    def ds_query(
        self,
        datasource_uid: str,
        expr: str,
        ref_id: str = "A",
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Execute a query against a datasource via Grafana API."""
        payload = {
            "queries": [
                {
                    "refId": ref_id,
                    "datasource": {"uid": datasource_uid, "type": "prometheus"},
                    "expr": expr,
                    "intervalMs": 15000,
                    "maxDataPoints": 100,
                }
            ],
            "from": "now-5m",
            "to": "now",
        }
        resp = requests.post(
            f"{self.base_url}/api/ds/query",
            auth=self.auth,
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()


class OTLPClient:
    """Client for sending synthetic OTLP telemetry to the collector."""

    def __init__(
        self,
        http_endpoint: str = "http://localhost:4318",
        grpc_endpoint: str = "http://localhost:4317",
    ):
        self.http_endpoint = http_endpoint.rstrip("/")
        self.grpc_endpoint = grpc_endpoint.rstrip("/")
        self._tracer = None
        self._meter = None

    # Lazy imports to keep startup cheap
    def _init_tracing(self, service_name: str = "acceptance-test") -> None:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": "1.0.0",
                "deployment.environment": "test",
            }
        )
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=f"{self.http_endpoint}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        self._tracer = provider.get_tracer(__name__)

    def _init_metrics(self, service_name: str = "acceptance-test") -> None:
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
            OTLPMetricExporter,
        )
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": "1.0.0",
                "deployment.environment": "test",
            }
        )
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=f"{self.http_endpoint}/v1/metrics"),
            export_interval_millis=1000,
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        self._meter = provider.get_meter(__name__)

    def send_trace(
        self,
        name: str = "test-trace",
        span_count: int = 3,
        attributes: Optional[dict[str, str]] = None,
    ) -> str:
        """Send a synthetic trace with child spans. Returns trace_id."""
        import uuid

        if self._tracer is None:
            self._init_tracing()

        test_id = str(uuid.uuid4())
        attrs = {"test_id": test_id, **(attributes or {})}

        with self._tracer.start_as_current_span(name) as parent:
            parent.set_attributes(attrs)
            trace_id = format(parent.get_span_context().trace_id, "032x")

            for i in range(span_count - 1):
                with self._tracer.start_as_current_span(f"{name}_child_{i}") as child:
                    child.set_attributes({**attrs, "span_index": str(i)})
                    time.sleep(0.005)

        return trace_id

    def send_counter(
        self,
        name: str = "test_counter",
        value: float = 1.0,
        attributes: Optional[dict[str, str]] = None,
    ) -> str:
        """Send a counter metric. Returns a test_id for correlation."""
        import uuid

        if self._meter is None:
            self._init_metrics()

        test_id = str(uuid.uuid4())
        attrs = {"test_id": test_id, **(attributes or {})}
        counter = self._meter.create_counter(name, description="Test counter", unit="1")
        counter.add(value, attrs)
        return test_id

    def send_histogram(
        self,
        name: str = "test_duration",
        value: float = 100.0,
        attributes: Optional[dict[str, str]] = None,
    ) -> str:
        """Send a histogram metric. Returns a test_id for correlation."""
        import uuid

        if self._meter is None:
            self._init_metrics()

        test_id = str(uuid.uuid4())
        attrs = {"test_id": test_id, **(attributes or {})}
        histogram = self._meter.create_histogram(
            name, description="Test histogram", unit="ms"
        )
        histogram.record(value, attrs)
        return test_id


# ──────────────────────────────────────────────────────────────────────
# ObservabilityStack — Main orchestration class
# ──────────────────────────────────────────────────────────────────────


class ObservabilityStack:
    """Manage the uFawkesObs Docker Compose stack and provide typed clients."""

    def __init__(
        self,
        compose_dir: Path | str = DEFAULT_COMPOSE_DIR,
        profiles: Optional[list[str]] = None,
        env: Optional[dict[str, str]] = None,
    ):
        self.compose_dir = Path(compose_dir).resolve()
        self.profiles = profiles or ["core"]
        self.env = env or {}
        self._evidence_dir: Optional[Path] = None

    # ── Lifecycle ──────────────────────────────────────────────────────

    def start(self, timeout: int = HEALTH_CHECK_TIMEOUT) -> StackHealth:
        """Start the Docker Compose stack and wait for health."""
        cmd = self._compose_cmd() + ["up", "-d"]
        subprocess.run(cmd, cwd=self.compose_dir, check=True, capture_output=True)
        return self.wait_for_healthy(timeout=timeout)

    def stop(self, volumes: bool = False) -> None:
        """Stop the Docker Compose stack."""
        cmd = self._compose_cmd() + ["down"]
        if volumes:
            cmd.append("-v")
        subprocess.run(cmd, cwd=self.compose_dir, check=True, capture_output=True)

    def restart_service(self, service: str) -> None:
        """Restart a single service."""
        cmd = self._compose_cmd() + ["up", "-d", "--force-recreate", service]
        subprocess.run(cmd, cwd=self.compose_dir, check=True, capture_output=True)

    def stop_service(self, service: str) -> None:
        """Stop a single service."""
        cmd = self._compose_cmd() + ["stop", service]
        subprocess.run(cmd, cwd=self.compose_dir, check=True, capture_output=True)

    def service_logs(self, service: str, tail: int = 50) -> str:
        """Get logs for a service."""
        cmd = self._compose_cmd() + ["logs", "--tail", str(tail), service]
        result = subprocess.run(
            cmd, cwd=self.compose_dir, capture_output=True, text=True
        )
        return result.stdout + result.stderr

    def service_status(self) -> str:
        """Get status of all services."""
        cmd = self._compose_cmd() + ["ps"]
        result = subprocess.run(
            cmd, cwd=self.compose_dir, capture_output=True, text=True
        )
        return result.stdout

    def is_service_running(self, service: str) -> bool:
        """Check if a specific service is running."""
        status = self.service_status()
        return (
            service in status and "Up" in status.split(service, 1)[1].split("\n")[0]
            if service in status
            else False
        )

    def _compose_cmd(self) -> list[str]:
        """Build the docker compose command with profiles."""
        cmd = ["docker", "compose"]
        for profile in self.profiles:
            cmd.extend(["--profile", profile])
        return cmd

    # ── Health Checks ──────────────────────────────────────────────────

    def wait_for_healthy(self, timeout: int = HEALTH_CHECK_TIMEOUT) -> StackHealth:
        """Wait for all configured services to be healthy.

        Checks health endpoints for services that have them, and falls back
        to checking if the container is running for services without HTTP health.
        """
        start = time.time()
        results: list[ServiceHealth] = []
        all_healthy = True

        for service, url in SERVICE_HEALTH_URLS.items():
            s_start = time.time()
            healthy = False
            status_code = 0
            error = ""

            while time.time() - start < timeout:
                try:
                    resp = requests.get(url, timeout=5)
                    status_code = resp.status_code
                    if status_code == 200:
                        healthy = True
                        break
                except requests.RequestException as e:
                    error = str(e)

                # For services without health endpoints, check docker compose ps
                if not healthy:
                    try:
                        out = subprocess.run(
                            self._compose_cmd()
                            + ["ps", "--format", "{{.Status}}", service],
                            cwd=self.compose_dir,
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if "Up" in out.stdout:
                            healthy = True
                    except subprocess.TimeoutExpired:
                        pass

                time.sleep(HEALTH_CHECK_INTERVAL)

            elapsed = time.time() - s_start
            if not healthy:
                all_healthy = False
            results.append(
                ServiceHealth(
                    name=service,
                    healthy=healthy,
                    elapsed=elapsed,
                    status_code=status_code,
                    error=error,
                )
            )

        return StackHealth(
            all_healthy=all_healthy,
            services=results,
            elapsed=time.time() - start,
        )

    def health_summary(self) -> str:
        """Quick health summary for diagnostics."""
        health = self.wait_for_healthy(timeout=30)
        return health.summary()

    # ── Typed Clients ──────────────────────────────────────────────────

    def promql(self) -> PromQLClient:
        """Get a PromQL client for querying Prometheus."""
        return PromQLClient()

    def loki(self) -> LokiClient:
        """Get a Loki client for querying logs."""
        return LokiClient()

    def tempo(self) -> TempoClient:
        """Get a Tempo client for querying traces."""
        return TempoClient()

    def grafana(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> GrafanaClient:
        """Get a Grafana client for querying dashboards and datasources."""
        return GrafanaClient(
            username=username or os.getenv("GRAFANA_ADMIN_USER", "admin"),
            password=password or os.getenv("GRAFANA_ADMIN_PASSWORD", "admin"),
        )

    def otlp(self) -> OTLPClient:
        """Get an OTLP client for sending synthetic telemetry."""
        return OTLPClient()

    # ── Evidence Capture ───────────────────────────────────────────────

    def set_evidence_dir(self, path: Path | str) -> None:
        """Set the directory for evidence output."""
        self._evidence_dir = Path(path)

    def capture_evidence(self, test_id: str, **artifacts: Any) -> Optional[Path]:
        """Capture evidence from a test for documentation generation."""
        if self._evidence_dir is None:
            return None
        evidence = Evidence(test_id=test_id)
        for key, value in artifacts.items():
            evidence.add(key, value)
        return evidence.save(self._evidence_dir)

    def capture_prometheus_targets(self) -> dict[str, Any]:
        """Capture Prometheus target inventory as evidence."""
        try:
            targets = self.promql().targets()
            summary = {
                "total": len(targets),
                "up": sum(1 for t in targets if t.get("health") == "up"),
                "down": sum(1 for t in targets if t.get("health") != "up"),
                "targets": [
                    {
                        "job": t.get("labels", {}).get("job"),
                        "instance": t.get("labels", {}).get("instance"),
                        "health": t.get("health"),
                    }
                    for t in targets
                ],
            }
            return summary
        except Exception as e:
            return {"error": str(e)}

    def capture_grafana_datasources(self) -> list[dict[str, Any]]:
        """Capture Grafana datasource inventory as evidence."""
        try:
            return [
                {"name": ds.get("name"), "type": ds.get("type"), "url": ds.get("url")}
                for ds in self.grafana().datasources()
            ]
        except Exception as e:
            return [{"error": str(e)}]


# ──────────────────────────────────────────────────────────────────────
# Default fixture instance (created by conftest.py)
# ──────────────────────────────────────────────────────────────────────

_default_stack: Optional[ObservabilityStack] = None


def get_default_stack() -> ObservabilityStack:
    """Get or create the default ObservabilityStack instance."""
    global _default_stack
    if _default_stack is None:
        _default_stack = ObservabilityStack()
    return _default_stack


def reset_default_stack() -> None:
    """Reset the default stack (useful for testing)."""
    global _default_stack
    _default_stack = None
