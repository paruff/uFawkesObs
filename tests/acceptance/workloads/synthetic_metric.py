"""
SyntheticMetricWorkload — generates realistic OTLP metrics for contract tests.

Produces counters and histograms with known increments and labels for
validating the full OTLP → OTel Collector → Prometheus → Grafana path.

The OTel Collector uses a Prometheus exporter on :8889 with namespace
"app_metrics". Counters receive a "_total" suffix from the Prometheus
exporter (OpenMetrics convention).
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


class SyntheticMetricWorkload:
    """Generates OTLP metrics for contract testing.

    Usage::

        workload = SyntheticMetricWorkload()
        test_id = workload.emit_counter("checkout_requests", value=1, labels={"tier": "gold"})
        # In Prometheus: app_metrics_checkout_requests_total{test_id="..."}

        test_id = workload.emit_histogram("request_duration", value=250.0)
        # In Prometheus: app_metrics_request_duration_count{test_id="..."}
        #                app_metrics_request_duration_sum{test_id="..."}
    """

    def __init__(
        self,
        otlp_http_endpoint: str = "http://localhost:4318",
        service_name: str = "acceptance-test-plane",
    ):
        self.otlp_http_endpoint = otlp_http_endpoint.rstrip("/")
        self.service_name = service_name
        self._meter = None
        self._cached_instruments: dict[str, Any] = {}

    def _init_metrics(self) -> None:
        """Lazy-init the OTel meter provider."""
        resource = Resource.create(
            {
                "service.name": self.service_name,
                "service.version": "2.0.0",
                "deployment.environment": "test",
            }
        )
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=f"{self.otlp_http_endpoint}/v1/metrics"),
            export_interval_millis=500,
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        self._meter = provider.get_meter(__name__)

    def emit_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None,
        known_test_id: Optional[str] = None,
    ) -> str:
        """Emit a counter metric. Returns test_id for correlation.

        The counter will appear in Prometheus as ``app_metrics_{name}_total``
        because the OTel Collector's prometheus exporter uses namespace "app_metrics".
        """
        if self._meter is None:
            self._init_metrics()

        test_id = known_test_id or str(uuid.uuid4())
        attrs = {"test_id": test_id, **(labels or {})}

        if name not in self._cached_instruments:
            self._cached_instruments[name] = self._meter.create_counter(
                name, description=f"Test counter: {name}", unit="1"
            )
        self._cached_instruments[name].add(value, attrs)
        return test_id

    def emit_histogram(
        self,
        name: str,
        value: float = 100.0,
        labels: Optional[dict[str, str]] = None,
        known_test_id: Optional[str] = None,
    ) -> str:
        """Emit a histogram metric. Returns test_id for correlation.

        The histogram will appear in Prometheus as ``app_metrics_{name}_bucket``,
        ``app_metrics_{name}_count``, and ``app_metrics_{name}_sum``.
        """
        if self._meter is None:
            self._init_metrics()

        test_id = known_test_id or str(uuid.uuid4())
        attrs = {"test_id": test_id, **(labels or {})}

        if name not in self._cached_instruments:
            self._cached_instruments[name] = self._meter.create_histogram(
                name, description=f"Test histogram: {name}", unit="ms"
            )
        self._cached_instruments[name].record(value, attrs)
        return test_id

    def emit_updown_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[dict[str, str]] = None,
    ) -> str:
        """Emit an up-down counter (can go negative). Shares test_id."""
        if self._meter is None:
            self._init_metrics()

        test_id = str(uuid.uuid4())
        attrs = {"test_id": test_id, **(labels or {})}

        if name not in self._cached_instruments:
            self._cached_instruments[name] = self._meter.create_up_down_counter(
                name, description=f"Test up-down counter: {name}", unit="1"
            )
        self._cached_instruments[name].add(value, attrs)
        return test_id
