"""
SyntheticTraceWorkload — generates realistic OTLP traces for contract tests.

Produces traces with 3-5 spans that simulate a web request pattern:
  - Root span: HTTP handler (e.g., "GET /api/orders")
  - Child span 1: Database query (e.g., "SELECT * FROM orders")
  - Child span 2: External API call (e.g., "POST /payment/process")
  - Child span 3+ : Additional processing steps

Each span carries OpenTelemetry semantic convention attributes so the
resulting traces exercise the full Tempo ingestion and query path.

Supports both HTTP and gRPC transport protocols for the OTLP exporter.
"""

from __future__ import annotations

import random
import time
import uuid
from typing import Any, Optional

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Lazy imports for exporter choice
_HTTP_EXPORTER = None
_GRPC_EXPORTER = None


def _get_http_exporter(endpoint: str):
    """Lazy load HTTP span exporter."""
    global _HTTP_EXPORTER
    if _HTTP_EXPORTER is None:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        _HTTP_EXPORTER = OTLPSpanExporter
    return _HTTP_EXPORTER(endpoint=f"{endpoint}/v1/traces")


def _get_grpc_exporter(endpoint: str):
    """Lazy load gRPC span exporter."""
    global _GRPC_EXPORTER
    if _GRPC_EXPORTER is None:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        _GRPC_EXPORTER = OTLPSpanExporter
    return _GRPC_EXPORTER(endpoint=endpoint, insecure=True)


class SyntheticTraceWorkload:
    """Generates realistic OTLP traces for contract testing.

    Usage::

        workload = SyntheticTraceWorkload(protocol="http")
        trace_id = workload.simulate_web_request()

        workload_grpc = SyntheticTraceWorkload(protocol="grpc")
        trace_id = workload_grpc.simulate_web_request()
    """

    REQUEST_PATTERNS: list[dict[str, Any]] = [
        {
            "route": "/api/orders",
            "method": "GET",
            "status": 200,
            "child_spans": [
                {
                    "name": "db.query.orders",
                    "attrs": {
                        "db.system": "postgresql",
                        "db.statement": "SELECT * FROM orders LIMIT 50",
                    },
                },
                {
                    "name": "ext.cache.get",
                    "attrs": {"cache.system": "redis", "cache.key": "orders:recent"},
                },
            ],
        },
        {
            "route": "/api/checkout",
            "method": "POST",
            "status": 201,
            "child_spans": [
                {
                    "name": "db.insert.order",
                    "attrs": {
                        "db.system": "postgresql",
                        "db.statement": "INSERT INTO orders (...) VALUES (...)",
                    },
                },
                {
                    "name": "ext.payment.process",
                    "attrs": {
                        "payment.provider": "stripe",
                        "payment.amount": random.randint(10, 999),
                    },
                },
                {
                    "name": "msg.queue.publish",
                    "attrs": {
                        "messaging.system": "rabbitmq",
                        "messaging.destination": "order.confirmed",
                    },
                },
            ],
        },
        {
            "route": "/api/users/me",
            "method": "GET",
            "status": 200,
            "child_spans": [
                {
                    "name": "db.query.user",
                    "attrs": {
                        "db.system": "postgresql",
                        "db.statement": "SELECT * FROM users WHERE id = ?",
                    },
                },
                {
                    "name": "ext.auth.verify",
                    "attrs": {"auth.provider": "oauth2", "auth.token_type": "bearer"},
                },
            ],
        },
    ]

    def __init__(
        self,
        otlp_endpoint: str = "http://localhost:4318",
        protocol: str = "http",
        service_name: str = "acceptance-test-plane",
    ):
        """Initialise the trace workload.

        Args:
            otlp_endpoint: OTLP endpoint. For HTTP: "http://host:port".
                           For gRPC: "host:port" (without protocol prefix).
            protocol: "http" (default, port 4318) or "grpc" (port 4317).
            service_name: OTel service.name attribute.
        """
        self.otlp_endpoint = otlp_endpoint.rstrip("/")
        self.protocol = protocol
        self.service_name = service_name
        self._tracer = None

    def _init_tracing(self) -> None:
        """Lazy-init the OTel tracer with the chosen protocol."""
        resource = Resource.create(
            {
                "service.name": self.service_name,
                "service.version": "2.0.0",
                "deployment.environment": "test",
                "telemetry.sdk.name": "opentelemetry",
                "telemetry.sdk.language": "python",
            }
        )

        if self.protocol == "grpc":
            # gRPC endpoint: host:port (e.g., "localhost:4317")
            exporter = _get_grpc_exporter(self.otlp_endpoint)
        else:
            # HTTP endpoint: http://host:port/v1/traces
            exporter = _get_http_exporter(self.otlp_endpoint)

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        self._tracer = provider.get_tracer(__name__)

    def simulate_web_request(
        self,
        pattern: Optional[int] = None,
        extra_attrs: Optional[dict[str, str]] = None,
    ) -> str:
        """Simulate a web request trace. Returns 32-char hex trace_id."""
        if self._tracer is None:
            self._init_tracing()

        if pattern is None:
            pattern = random.randrange(len(self.REQUEST_PATTERNS))
        req = self.REQUEST_PATTERNS[pattern]

        test_id = str(uuid.uuid4())
        attrs: dict[str, str] = {
            "test_id": test_id,
            **(extra_attrs or {}),
        }

        with self._tracer.start_as_current_span(
            f"{req['method']} {req['route']}"
        ) as root:
            root.set_attributes(
                {
                    "http.method": req["method"],
                    "http.route": req["route"],
                    "http.status_code": req["status"],
                    **attrs,
                }
            )
            trace_id = format(root.get_span_context().trace_id, "032x")

            for child in req["child_spans"]:
                with self._tracer.start_as_current_span(child["name"]) as child_span:
                    child_span.set_attributes({**child["attrs"], **attrs})
                    time.sleep(0.005 * random.random())

        return trace_id

    def simulate_batch_job(self) -> str:
        """Simulate a batch processing trace with 4 spans."""
        if self._tracer is None:
            self._init_tracing()

        test_id = str(uuid.uuid4())
        with self._tracer.start_as_current_span("batch.process") as root:
            root.set_attributes(
                {
                    "job.name": "nightly-report",
                    "job.iteration": str(random.randint(1, 100)),
                    "test_id": test_id,
                }
            )
            trace_id = format(root.get_span_context().trace_id, "032x")

            with self._tracer.start_as_current_span("batch.load_data") as s1:
                s1.set_attributes(
                    {
                        "db.system": "postgresql",
                        "db.statement": "SELECT * FROM events WHERE date = CURRENT_DATE",
                        "test_id": test_id,
                    }
                )
                time.sleep(0.01)

            with self._tracer.start_as_current_span("batch.transform") as s2:
                s2.set_attributes(
                    {
                        "transformer.type": "aggregation",
                        "transformer.records_in": str(random.randint(100, 1000)),
                        "test_id": test_id,
                    }
                )
                time.sleep(0.005)

            with self._tracer.start_as_current_span("batch.export") as s3:
                s3.set_attributes(
                    {
                        "export.format": "parquet",
                        "export.path": f"/data/reports/report-{random.randint(1, 100)}.parquet",
                        "test_id": test_id,
                    }
                )
                time.sleep(0.005)

        return trace_id
