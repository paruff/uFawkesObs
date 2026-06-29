"""
SyntheticLogWorkload — generates structured JSON logs via OTLP logs signal.

Sends log records through the OTel Collector's OTLP receiver to the
Loki log storage backend. Each log has a structured JSON body with
well-known fields, plus OTel attributes for correlation.

The OTel Collector is configured with a ``logs`` pipeline:
  receivers: [otlp] → processors: [memory_limiter, batch] → exporters: [loki, debug]
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Optional

from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


class SyntheticLogWorkload:
    """Generates structured JSON logs via the OTLP logs signal.

    Usage::

        workload = SyntheticLogWorkload()
        test_id = workload.emit_log(
            body={"event": "order_created", "order_id": 12345},
            severity_text="INFO",
        )
        # In Loki: {test_id="..."} | json
    """

    LOG_PATTERNS: list[dict[str, Any]] = [
        {
            "body": {
                "event": "http_request",
                "method": "GET",
                "route": "/api/orders",
                "status": 200,
                "duration_ms": 42,
            },
            "severity_text": "INFO",
        },
        {
            "body": {
                "event": "db_query",
                "query": "SELECT * FROM orders",
                "rows_returned": 50,
                "duration_ms": 12,
            },
            "severity_text": "DEBUG",
        },
        {
            "body": {
                "event": "user_login",
                "user_id": "user_abc123",
                "auth_method": "oauth2",
                "success": True,
            },
            "severity_text": "INFO",
        },
        {
            "body": {
                "event": "payment_failed",
                "order_id": "ord_999",
                "reason": "card_declined",
                "amount": 4999,
            },
            "severity_text": "ERROR",
        },
        {
            "body": {
                "event": "health_check",
                "service": "api-gateway",
                "healthy": True,
                "uptime_seconds": 3600,
            },
            "severity_text": "INFO",
        },
    ]

    def __init__(
        self,
        otlp_http_endpoint: str = "http://localhost:4318",
        service_name: str = "acceptance-test-plane",
    ):
        self.otlp_http_endpoint = otlp_http_endpoint.rstrip("/")
        self.service_name = service_name
        self._logger = None

    def _init_logging(self) -> None:
        """Lazy-init the OTel LoggerProvider with OTLP export."""
        resource = Resource.create(
            {
                "service.name": self.service_name,
                "service.version": "2.0.0",
                "deployment.environment": "test",
            }
        )
        exporter = OTLPLogExporter(endpoint=f"{self.otlp_http_endpoint}/v1/logs")
        provider = LoggerProvider(resource=resource)
        provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        self._logger = provider.get_logger(__name__)

    def emit_log(
        self,
        body: dict[str, Any],
        severity_text: str = "INFO",
        severity_number: Optional[int] = None,
        extra_attributes: Optional[dict[str, str]] = None,
    ) -> str:
        """Emit a structured JSON log entry. Returns test_id for correlation.

        The body dict is serialized to JSON before sending.
        In Loki, use: ``{test_id="<value>"} | json`` to parse the body.
        """
        if self._logger is None:
            self._init_logging()

        test_id = str(uuid.uuid4())
        attrs = {"test_id": test_id, **(extra_attributes or {})}

        # Map severity text to OTel severity number
        sev_map = {
            "TRACE": 1,
            "DEBUG": 5,
            "INFO": 9,
            "WARN": 13,
            "WARNING": 13,
            "ERROR": 17,
            "FATAL": 21,
        }
        sev_num = severity_number or sev_map.get(severity_text.upper(), 9)

        self._logger.emit(
            body=json.dumps(body, default=str),
            severity_text=severity_text,
            severity_number=sev_num,
            attributes=attrs,
        )

        return test_id

    def emit_random_log(self) -> tuple[str, dict[str, Any]]:
        """Emit a random log pattern. Returns (test_id, body_dict)."""
        import random

        pattern = random.choice(self.LOG_PATTERNS)
        test_id = self.emit_log(
            body=pattern["body"],
            severity_text=pattern["severity_text"],
        )
        return test_id, pattern["body"]

    def emit_service_health_log(self) -> str:
        """Emit a health-status log entry."""
        return self.emit_log(
            body={
                "event": "service_status",
                "service": self.service_name,
                "healthy": True,
                "timestamp_epoch": time.time(),
            },
            severity_text="INFO",
            extra_attributes={"event_type": "health"},
        )
