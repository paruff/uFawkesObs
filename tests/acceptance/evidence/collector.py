# SPDX-License-Identifier: Apache-2.0
"""
Evidence Collector for uFawkesObs Acceptance Tests.

Provides a centralized mechanism for capturing structured test evidence
that feeds into runbook generation, SLO reports, and documentation.

Each piece of evidence is saved as a JSON artifact with metadata, and an
index file tracks all artifacts for a test run.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EvidenceArtifact:
    """A single piece of test evidence with metadata."""

    artifact_id: str
    artifact_type: str  # "otlp_payload", "grafana_response", "prometheus_targets", etc.
    timestamp: str
    test_name: str
    metadata: dict[str, Any]
    data: Any


class EvidenceCollector:
    """
    Collects and stores test evidence as structured JSON artifacts.

    Usage:
        collector = EvidenceCollector("reports/acceptance-full-evidence")
        collector.capture_otlp_payload("POST /v1/traces", trace_payload,
                                       test_name="test_contract_trace",
                                       description="Trace from external plane")
        collector.capture_grafana_response("Prometheus", "up{job=~\"otel.*\"}",
                                           response_data, test_name="test_dashboard")
        index = collector.finalize()
    """

    def __init__(self, evidence_dir: str | Path):
        """
        Initialize the evidence collector.

        Args:
            evidence_dir: Directory where evidence artifacts and index will be stored.
                         Subdirectories 'artifacts' and index.json will be created.
        """
        self.evidence_dir = Path(evidence_dir)
        self.artifacts_dir = self.evidence_dir / "artifacts"
        self.index_path = self.evidence_dir / "index.json"

        # Create directories
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Initialize index
        self._index = {
            "run_id": str(uuid.uuid4())[:8],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "artifacts": [],
        }

        # Save initial index
        self._save_index()

    def _save_index(self) -> None:
        """Save the current index to disk."""
        self.index_path.write_text(json.dumps(self._index, indent=2, default=str))

    def _add_artifact(self, artifact: EvidenceArtifact) -> None:
        """Add an artifact to the index and save its data."""
        # Save artifact data
        artifact_path = (
            self.artifacts_dir / f"{artifact.artifact_type}_{artifact.artifact_id}.json"
        )
        artifact_path.write_text(
            json.dumps(
                {
                    "artifact_id": artifact.artifact_id,
                    "artifact_type": artifact.artifact_type,
                    "timestamp": artifact.timestamp,
                    "test_name": artifact.test_name,
                    "metadata": artifact.metadata,
                    "data": artifact.data,
                },
                indent=2,
                default=str,
            )
        )

        # Update index
        self._index["artifacts"].append(
            {
                "artifact_id": artifact.artifact_id,
                "artifact_type": artifact.artifact_type,
                "timestamp": artifact.timestamp,
                "test_name": artifact.test_name,
                "metadata": artifact.metadata,
                "path": str(artifact_path.relative_to(self.evidence_dir)),
            }
        )
        self._save_index()

    # ── Capture Methods ────────────────────────────────────────────────

    def capture_otlp_payload(
        self,
        endpoint: str,
        payload: dict[str, Any],
        test_name: str,
        description: str = "OTLP payload",
        signal: str = "traces",  # "traces" | "metrics" | "logs"
    ) -> str:
        """
        Capture an OTLP payload (request or response).

        Args:
            endpoint: The OTLP endpoint (e.g., "otel-collector:4317")
            payload: The full OTLP JSON payload
            test_name: Name of the test capturing this evidence
            description: Human-readable description
            signal: The telemetry signal type

        Returns:
            The artifact ID for reference
        """
        artifact_id = str(uuid.uuid4())[:12]
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type="otlp_payload",
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_name=test_name,
            metadata={
                "endpoint": endpoint,
                "signal": signal,
                "description": description,
                "payload_size_bytes": len(json.dumps(payload, default=str)),
            },
            data=payload,
        )
        self._add_artifact(artifact)
        return artifact_id

    def capture_grafana_response(
        self,
        datasource: str,
        query: str,
        response: dict[str, Any],
        test_name: str,
        description: str = "Grafana API response",
        panel_uid: str | None = None,
    ) -> str:
        """
        Capture a Grafana API response (dashboard panel, Explore query, etc.).

        Args:
            datasource: The Grafana datasource name (Prometheus, Loki, Tempo, Alertmanager)
            query: The query that was executed
            response: The full Grafana API response
            test_name: Name of the test capturing this evidence
            description: Human-readable description
            panel_uid: Optional panel UID if from a dashboard panel

        Returns:
            The artifact ID for reference
        """
        artifact_id = str(uuid.uuid4())[:12]
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type="grafana_response",
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_name=test_name,
            metadata={
                "datasource": datasource,
                "query": query,
                "description": description,
                "panel_uid": panel_uid,
                "response_size_bytes": len(json.dumps(response, default=str)),
            },
            data=response,
        )
        self._add_artifact(artifact)
        return artifact_id

    def capture_prometheus_targets(
        self,
        targets: list[dict[str, Any]],
        test_name: str,
        description: str = "Prometheus scrape target inventory",
    ) -> str:
        """
        Capture Prometheus scrape target inventory.

        Args:
            targets: List of target objects from Prometheus /api/v1/targets
            test_name: Name of the test capturing this evidence
            description: Human-readable description

        Returns:
            The artifact ID for reference
        """
        artifact_id = str(uuid.uuid4())[:12]
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type="prometheus_targets",
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_name=test_name,
            metadata={
                "description": description,
                "target_count": len(targets),
                "up_count": sum(1 for t in targets if t.get("health") == "up"),
            },
            data=targets,
        )
        self._add_artifact(artifact)
        return artifact_id

    def capture_chaos_event(
        self,
        event_type: str,
        service: str,
        description: str,
        test_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Capture a chaos test event for recovery timeline.

        Args:
            event_type: "failure_start", "failure_end", "recovery_start", "recovery_end", "metric"
            service: The service affected (loki, prometheus, otel-collector, etc.)
            description: Human-readable description of the event
            test_name: Name of the test capturing this evidence
            metadata: Additional metadata (duration, data loss metrics, etc.)

        Returns:
            The artifact ID for reference
        """
        artifact_id = str(uuid.uuid4())[:12]
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type="chaos_event",
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_name=test_name,
            metadata={
                "event_type": event_type,
                "service": service,
                "description": description,
                **(metadata or {}),
            },
            data={
                "phase": event_type,
                "service": service,
                "description": description,
            },
        )
        self._add_artifact(artifact)
        return artifact_id

    def capture_slo_measurement(
        self,
        sli_id: str,
        sli_name: str,
        measured_ms: float,
        slo_threshold_ms: float,
        passed: bool,
        test_name: str,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """
        Capture an SLO measurement result.

        Args:
            sli_id: The SLI identifier (e.g., "OBS-SLI-001")
            sli_name: Human-readable SLI name
            measured_ms: Measured value in milliseconds
            slo_threshold_ms: SLO threshold in milliseconds
            passed: Whether the measurement passed the SLO
            test_name: Name of the test capturing this evidence
            extra: Additional data (e.g., latency histogram, raw samples)

        Returns:
            The artifact ID for reference
        """
        artifact_id = str(uuid.uuid4())[:12]
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type="slo_measurement",
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_name=test_name,
            metadata={
                "sli_id": sli_id,
                "sli_name": sli_name,
                "measured_ms": measured_ms,
                "slo_threshold_ms": slo_threshold_ms,
                "passed": passed,
            },
            data={
                "sli_id": sli_id,
                "sli_name": sli_name,
                "measured_ms": measured_ms,
                "slo_threshold_ms": slo_threshold_ms,
                "passed": passed,
                "extra": extra or {},
            },
        )
        self._add_artifact(artifact)
        return artifact_id

    def capture_dashboard_validation(
        self,
        dashboard_uid: str,
        dashboard_title: str,
        panel_results: list[dict[str, Any]],
        test_name: str,
    ) -> str:
        """
        Capture dashboard panel validation results.

        Args:
            dashboard_uid: Grafana dashboard UID
            dashboard_title: Dashboard title
            panel_results: List of panel validation results with query, has_data, etc.
            test_name: Name of the test capturing this evidence

        Returns:
            The artifact ID for reference
        """
        artifact_id = str(uuid.uuid4())[:12]
        artifact = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type="dashboard_validation",
            timestamp=datetime.now(timezone.utc).isoformat(),
            test_name=test_name,
            metadata={
                "dashboard_uid": dashboard_uid,
                "dashboard_title": dashboard_title,
                "panel_count": len(panel_results),
                "panels_with_data": sum(
                    1 for p in panel_results if p.get("has_data", False)
                ),
            },
            data={
                "dashboard_uid": dashboard_uid,
                "dashboard_title": dashboard_title,
                "panel_results": panel_results,
            },
        )
        self._add_artifact(artifact)
        return artifact_id

    # ── Finalization ──────────────────────────────────────────────────

    def finalize(self) -> dict[str, Any]:
        """
        Finalize the evidence collection and return the complete index.

        Returns:
            The complete index dictionary
        """
        self._index["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._index["total_artifacts"] = len(self._index["artifacts"])
        self._save_index()
        return self._index


def get_evidence_collector(request) -> EvidenceCollector:
    """
    Pytest fixture factory for getting an EvidenceCollector instance.

    Usage in test:
        def test_my_feature(evidence_collector):
            evidence_collector.capture_otlp_payload(...)

    Requires --evidence-dir CLI option to be set.
    """
    evidence_dir = request.config.getoption("--evidence-dir")
    if not evidence_dir:
        # Return a no-op collector if no evidence dir specified
        return _NoOpCollector()

    return EvidenceCollector(evidence_dir)


class _NoOpCollector:
    """No-op collector for when evidence collection is disabled."""

    def capture_otlp_payload(self, *args, **kwargs) -> str:
        return "noop"

    def capture_grafana_response(self, *args, **kwargs) -> str:
        return "noop"

    def capture_prometheus_targets(self, *args, **kwargs) -> str:
        return "noop"

    def capture_chaos_event(self, *args, **kwargs) -> str:
        return "noop"

    def capture_slo_measurement(self, *args, **kwargs) -> str:
        return "noop"

    def capture_dashboard_validation(self, *args, **kwargs) -> str:
        return "noop"

    def finalize(self) -> dict:
        return {"noop": True}


# For backward compatibility
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evidence Collector CLI")
    parser.add_argument("--evidence-dir", required=True, help="Evidence directory")
    parser.add_argument("--test-name", required=True, help="Test name")
    args = parser.parse_args()

    # Simple demo
    collector = EvidenceCollector(args.evidence_dir)
    collector.capture_otlp_payload(
        endpoint="otel-collector:4317",
        payload={"resourceSpans": []},
        test_name=args.test_name,
        description="Demo OTLP payload",
    )
    print(f"Evidence saved to {args.evidence_dir}")
    print(json.dumps(collector.finalize(), indent=2))
