"""
DORA Event Generator for uFawkesObs Acceptance Tests

Simulates deployment, incident, and lead-time spans for DORA metrics testing.

Each scenario generates realistic OTLP traces with semantic attributes for DORA evaluation.
"""

from __future__ import annotations

import time
import uuid

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource


def _get_exporter(protocol: str, endpoint: str):
    """Lazy-load the appropriate OTLP exporter based on protocol."""
    if protocol == "http":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        return BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
    else:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        return BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))


class DORAWorkload:
    """Generates traces for DORA metrics (deployment, incident, lead-time).

    Usage::

        workload = DORAWorkload(otlp_endpoint="localhost:4317", protocol="grpc")
        trace_id = workload.simulate_deployment(instance="prod-001")
        trace_id = workload.simulate_incident(severity="major")
        trace_id = workload.simulate_lead_time(duration_ms=60000)
    """

    def __init__(
        self,
        otlp_endpoint: str = "http://localhost:4318",
        protocol: str = "http",
        service_name: str = "acceptance-test-plane",
    ):
        self.otlp_endpoint = otlp_endpoint.rstrip("/")
        self.protocol = protocol
        self.service_name = service_name
        self._tracer = None

    def _init_tracing(self) -> None:
        """Configure the OTel tracer with DORA attributes."""
        resource = Resource.create(
            {
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": "test",
            }
        )
        exporter = _get_exporter(self.protocol, self.otlp_endpoint)
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(exporter)
        self._tracer = provider.get_tracer(__name__)

    def simulate_deployment(self, instance: str = "default") -> str:
        """Generate a deployment trace with instance-specific attributes.

        Args:
            instance: Target deployment instance identifier.

        Returns:
            The 32-character hex trace_id.
        """
        if self._tracer is None:
            self._init_tracing()

        trace_id = str(uuid.uuid4())
        with self._tracer.start_as_current_span(
            "deployment",
            attributes={"phase": "rolling", "instance": instance},
        ) as span:
            time.sleep(0.05)
            span.set_attributes({"status": "success"})

        return trace_id

    def simulate_incident(self, severity: str = "minor", impact: str = "low") -> str:
        """Generate an incident trace with severity and impact attributes.

        Args:
            severity: Incident severity (minor, major, critical).
            impact: Impact level (low, medium, high).

        Returns:
            The 32-character hex trace_id.
        """
        if self._tracer is None:
            self._init_tracing()

        trace_id = str(uuid.uuid4())
        with self._tracer.start_as_current_span(
            "incident",
            attributes={"severity": severity, "impact": impact},
        ) as span:
            time.sleep(0.1 if severity == "critical" else 0.01)
            if severity == "critical":
                span.set_attributes({"outcome": "resolved"})

        return trace_id

    def simulate_lead_time(self, duration_ms: int = 300) -> str:
        """Generate a lead-time span for change-to-deployment time.

        Args:
            duration_ms: Simulated lead time in milliseconds.

        Returns:
            The 32-character hex trace_id.
        """
        if self._tracer is None:
            self._init_tracing()

        trace_id = str(uuid.uuid4())
        with self._tracer.start_as_current_span(
            "lead_time_span",
            attributes={"change_id": str(uuid.uuid4()), "duration_ms": duration_ms},
        ) as span:
            time.sleep(duration_ms / 1000)
            span.set_attributes({"duration_ms": duration_ms})

        return trace_id
