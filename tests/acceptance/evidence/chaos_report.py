"""
Chaos Test Evidence Reporter.

Generates recovery timeline evidence from chaos test executions.
Outputs Mermaid sequence diagrams for incident response runbooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ChaosEvent:
    """A single event in a chaos test timeline."""

    timestamp: str
    event_type: str  # "failure_start", "failure_end", "recovery_start", "recovery_end", "metric"
    service: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ChaosReportGenerator:
    """Generates chaos test evidence reports.

    Collects events from chaos tests and produces:
      - Mermaid sequence diagrams for recovery timelines
      - Markdown evidence reports
      - Data loss metrics
    """

    def __init__(self):
        self.events: list[ChaosEvent] = []
        self.generated_at = datetime.now(timezone.utc)

    def add_event(self, event: ChaosEvent | dict[str, Any]) -> None:
        """Add a chaos event to the report."""
        if isinstance(event, dict):
            self.events.append(ChaosEvent(**event))
        else:
            self.events.append(event)

    def generate_mermaid_sequence(self) -> str:
        """Generate a Mermaid sequence diagram from chaos events."""
        lines = [
            "```mermaid",
            "sequenceDiagram",
            "    participant U as User",
            "    participant O as OTel Collector",
            "    participant P as Prometheus",
            "    participant L as Loki",
            "    participant T as Tempo",
            "    participant G as Grafana",
            "",
        ]

        for event in self.events:
            actor = self._get_actor_for_service(event.service)
            msg = event.description
            if event.event_type == "failure_start":
                lines.append("    rect rgb(255, 200, 200)")
                lines.append(f"    {actor}->>{actor}: ⚠️ {msg}")
            elif event.event_type == "failure_end":
                lines.append("    end")
                lines.append(f"    {actor}->>{actor}: ✅ {msg}")
            elif event.event_type == "recovery_start":
                lines.append(f"    {actor}->>{actor}: 🔄 {msg}")
            elif event.event_type == "recovery_end":
                lines.append(f"    {actor}->>{actor}: ✅ {msg}")
            else:
                lines.append(f"    {actor}->>{actor}: {msg}")

        lines.append("```")
        return "\n".join(lines)

    def _get_actor_for_service(self, service: str) -> str:
        """Map service name to Mermaid actor alias."""
        mapping = {
            "otel-collector": "O",
            "prometheus": "P",
            "loki": "L",
            "tempo": "T",
            "grafana": "G",
            "alloy": "A",
            "alertmanager": "AM",
        }
        return mapping.get(service, service.upper()[:2])

    def generate_markdown_report(self) -> str:
        """Generate a markdown evidence report."""
        lines = [
            "# Chaos Test Evidence Report",
            "",
            f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## Event Timeline",
            "",
            "| Timestamp | Service | Event | Description |",
            "|-----------|---------|-------|-------------|",
        ]

        for event in self.events:
            lines.append(
                f"| {event.timestamp} | {event.service} | {event.event_type} | {event.description} |"
            )

        lines.extend(
            [
                "",
                "## Recovery Timeline (Mermaid)",
                "",
                self.generate_mermaid_sequence(),
                "",
                "## Data Loss Summary",
                "",
                "_Coming soon: Data loss metrics from log/metric/trace buffers_",
                "",
            ]
        )

        return "\n".join(lines)


if __name__ == "__main__":
    # CLI entry point for chaos evidence generation
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate chaos test evidence report")
    parser.add_argument(
        "--events",
        type=str,
        default=None,
        help="JSON file with chaos events",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/chaos-report.md",
        help="Output path for markdown report",
    )
    args = parser.parse_args()

    report = ChaosReportGenerator()

    if args.events:
        with open(args.events) as f:
            events = json.load(f)
            for event in events:
                report.add_event(event)

    output_path = args.output
    with open(output_path, "w") as f:
        f.write(report.generate_markdown_report())

    print(f"✅ Chaos report saved: {output_path}")
