#!/usr/bin/env python3
"""
Runbook Snippet Generator for uFawkesObs.

Converts test evidence into actionable runbook examples and troubleshooting guides.
Run after post-merge acceptance tests to generate documentation snippets.

Usage:
    python tests/acceptance/evidence/generate_runbook.py \
        --evidence-dir reports/acceptance-full-evidence \
        --output reports/runbook-snippets.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RunbookGenerator:
    """
    Generates runbook snippets from acceptance test evidence.

    Produces markdown that can be included in:
      - docs/runbooks/troubleshooting.md
      - docs/onboarding/external-plane-integration.md
      - Weekly platform review documents
    """

    def __init__(self, evidence_dir: Path):
        """
        Initialize with evidence directory.

        Args:
            evidence_dir: Path to directory containing evidence artifacts
        """
        self.evidence_dir = Path(evidence_dir)
        self.artifacts_dir = self.evidence_dir / "artifacts"
        self.index_path = self.evidence_dir / "index.json"

        self.otlp_payloads: list[dict[str, Any]] = []
        self.grafana_responses: list[dict[str, Any]] = []
        self.prometheus_targets: list[dict[str, Any]] = []
        self.chaos_events: list[dict[str, Any]] = []
        self.slo_measurements: list[dict[str, Any]] = []
        self.dashboard_validations: list[dict[str, Any]] = []

    def load_evidence(self) -> None:
        """Load all evidence artifacts from the evidence directory."""
        if not self.index_path.exists():
            print(f"⚠️  No index found at {self.index_path}")
            return

        index = json.loads(self.index_path.read_text())
        for artifact_info in index.get("artifacts", []):
            artifact_type = artifact_info["artifact_type"]
            artifact_id = artifact_info["artifact_id"]

            artifact_path = self.artifacts_dir / f"{artifact_type}_{artifact_id}.json"
            if not artifact_path.exists():
                continue

            try:
                artifact = json.loads(artifact_path.read_text())
                data = artifact.get("data", {})
                metadata = artifact.get("metadata", {})

                if artifact_type == "otlp_payload":
                    self.otlp_payloads.append({"metadata": metadata, "data": data})
                elif artifact_type == "grafana_response":
                    self.grafana_responses.append({"metadata": metadata, "data": data})
                elif artifact_type == "prometheus_targets":
                    self.prometheus_targets.append({"metadata": metadata, "data": data})
                elif artifact_type == "chaos_event":
                    self.chaos_events.append({"metadata": metadata, "data": data})
                elif artifact_type == "slo_measurement":
                    self.slo_measurements.append({"metadata": metadata, "data": data})
                elif artifact_type == "dashboard_validation":
                    self.dashboard_validations.append(
                        {"metadata": metadata, "data": data}
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️  Failed to load artifact {artifact_id}: {e}")

    # ── Section Generators ─────────────────────────────────────────────

    def generate_header(self) -> str:
        """Generate the runbook header."""
        return f"""# Debugging & Troubleshooting Runbook Snippets

**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
**Source:** uFawkesObs Post-Merge Acceptance Tests
**Evidence Directory:** `{self.evidence_dir}`

> These snippets are auto-generated from passing acceptance tests. They represent
> known-good configurations, expected query patterns, and measured system behavior.
> Use them as starting points for troubleshooting and onboarding.

---

"""

    def generate_otlp_payload_section(self) -> str:
        """Generate OTLP payload examples section."""
        if not self.otlp_payloads:
            return ""

        lines = [
            "## Example OTLP Payloads (from Contract Tests)\n",
            "Use these as reference when debugging telemetry ingestion from external planes.\n",
        ]

        for i, payload in enumerate(self.otlp_payloads[:3]):  # Limit to 3 examples
            meta = payload.get("metadata", {})
            data = payload.get("data", {})
            source = meta.get("source", "unknown")
            desc = meta.get("description", "OTLP payload")

            lines.append(f"### Example {i + 1}: {desc} (`{source}`)\n")
            lines.append("```json")
            lines.append(json.dumps(data, indent=2, default=str))
            lines.append("```\n")

        return "\n".join(lines) + "\n---\n"

    def generate_grafana_query_section(self) -> str:
        """Generate Grafana query examples section."""
        if not self.grafana_responses:
            return ""

        lines = [
            "## Grafana Query Patterns (from Dashboard Validation)\n",
            "These queries returned data in the latest post-merge acceptance run.\n",
        ]

        # Group by datasource
        by_datasource: dict[str, list[dict]] = {}
        for resp in self.grafana_responses:
            data = resp.get("data", {})
            ds = data.get("datasource", "unknown")
            if ds not in by_datasource:
                by_datasource[ds] = []
            by_datasource[ds].append(resp)

        for datasource, responses in by_datasource.items():
            lines.append(f"### Datasource: {datasource}\n")
            for resp in responses[:2]:  # Limit to 2 per datasource
                data = resp.get("data", {})
                query = data.get("query", "")
                meta = resp.get("metadata", {})
                desc = meta.get("description", "Grafana query")

                if query:
                    lines.append(f"**{desc}**")
                    lines.append("```promql")
                    lines.append(query)
                    lines.append("```")
                    lines.append("")

        return "\n".join(lines) + "\n---\n"

    def generate_prometheus_targets_section(self) -> str:
        """Generate Prometheus target inventory section."""
        if not self.prometheus_targets:
            return ""

        lines = [
            "## Prometheus Scrape Target Inventory\n",
            "Current scrape targets as of the last post-merge acceptance run.\n",
            "Use this to verify all expected targets are configured.\n",
        ]

        for target_artifact in self.prometheus_targets:
            data = target_artifact.get("data", [])
            if isinstance(data, list):
                active_targets = [t for t in data if t.get("health") == "up"]
                lines.append(
                    f"\n### Active Targets ({len(active_targets)}/{len(data)})\n"
                )
                lines.append("| Target | Job | Instance | Labels |")
                lines.append("|--------|-----|----------|--------|")
                for target in active_targets[:15]:  # Limit to 15
                    labels = target.get("labels", {})
                    job = labels.get("job", "unknown")
                    instance = target.get("scrapeUrl", "unknown")
                    label_str = ", ".join(
                        f"{k}={v}"
                        for k, v in labels.items()
                        if k not in ["job", "instance"]
                    )
                    lines.append(f"| {instance} | {job} | {instance} | {label_str} |")

        return "\n".join(lines) + "\n---\n"

    def generate_slo_section(self) -> str:
        """Generate SLO compliance section."""
        if not self.slo_measurements:
            return ""

        lines = [
            "## SLO Compliance (Latest Measurements)\n",
            "Measured during the latest post-merge acceptance test run.\n",
        ]

        # Group by SLI
        by_sli: dict[str, list] = {}
        for m in self.slo_measurements:
            data = m.get("data", {})
            sli_id = data.get("sli_id", "unknown")
            if sli_id not in by_sli:
                by_sli[sli_id] = []
            by_sli[sli_id].append(m)

        lines.append("| SLI | Name | Measured | Threshold | Status |")
        lines.append("|-----|------|----------|-----------|--------|")

        for sli_id, measurements in by_sli.items():
            latest = measurements[-1]
            data = latest.get("data", {})
            name = data.get("sli_name", sli_id)
            measured = data.get("measured_ms", 0)
            threshold = data.get("slo_threshold_ms", 0)
            passed = data.get("passed", False)
            status = "✅ PASS" if passed else "❌ FAIL"
            lines.append(
                f"| {sli_id} | {name} | {measured:.0f}ms | {threshold:.0f}ms | {status} |"
            )

        return "\n".join(lines) + "\n---\n"

    def generate_chaos_recovery_section(self) -> str:
        """Generate chaos recovery timeline section."""
        if not self.chaos_events:
            return ""

        lines = [
            "## Chaos Recovery Timelines\n",
            "Recovery measurements from nightly chaos tests.\n",
        ]

        # Group by chaos scenario
        by_scenario: dict[str, list] = {}
        for event in self.chaos_events:
            data = event.get("data", {})
            tags = event.get("metadata", {}).get("tags", [])
            scenario = next(
                (
                    t
                    for t in tags
                    if t
                    in [
                        "loki_restart",
                        "prometheus_restart",
                        "otel_collector_restart",
                        "network_partition",
                        "grafana_datasource_loss",
                    ]
                ),
                "unknown",
            )
            if scenario not in by_scenario:
                by_scenario[scenario] = []
            by_scenario[scenario].append(event)

        for scenario, events in by_scenario.items():
            lines.append(f"\n### Scenario: {scenario}\n")
            lines.append("| Phase | Timestamp | Details |")
            lines.append("|-------|-----------|---------|")

            for event in events:
                data = event.get("data", {})
                meta = event.get("metadata", {})
                phase = data.get("phase", "unknown")
                timestamp = meta.get("timestamp", "unknown")[:19]
                details = data.get("description", str(data))
                lines.append(f"| {phase} | {timestamp} | {details} |")

        return "\n".join(lines) + "\n---\n"

    def generate_dashboard_section(self) -> str:
        """Generate dashboard validation section."""
        if not self.dashboard_validations:
            return ""

        lines = [
            "## Dashboard Panel Validation\n",
            "Panels that returned data in the latest acceptance test run.\n",
        ]

        for dv in self.dashboard_validations:
            data = dv.get("data", {})
            uid = data.get("dashboard_uid", "unknown")
            title = data.get("dashboard_title", "Unknown Dashboard")
            panels = data.get("panel_results", [])

            lines.append(f"\n### {title} (`{uid}`)\n")
            lines.append(f"Panels validated: {len(panels)}\n")

            for panel in panels[:5]:  # Limit to 5 panels
                panel_title = panel.get("title", "Untitled")
                query = panel.get("query", "")
                has_data = panel.get("has_data", False)
                status = "✅" if has_data else "❌"
                lines.append(f"- {status} **{panel_title}**")
                if query:
                    lines.append("  ```promql")
                    lines.append(f"  {query}")
                    lines.append("  ```")

        return "\n".join(lines) + "\n---\n"

    def generate_footer(self) -> str:
        """Generate the runbook footer."""
        return """## Integration with Documentation

To include these snippets in official docs:

```markdown
<!-- In docs/runbooks/troubleshooting.md -->
{% include 'runbook-snippets.md' start='## Example OTLP Payloads' end='---' %}
```

---

*Generated by `tests/acceptance/evidence/generate_runbook.py`*
*Part of uFawkesObs Phase 6: Evidence Pipeline & Documentation*
"""

    def generate_full_report(self) -> str:
        """Generate the complete runbook snippet report."""
        self.load_evidence()

        sections = [
            self.generate_header(),
            self.generate_otlp_payload_section(),
            self.generate_grafana_query_section(),
            self.generate_prometheus_targets_section(),
            self.generate_slo_section(),
            self.generate_chaos_recovery_section(),
            self.generate_dashboard_section(),
            self.generate_footer(),
        ]

        return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(
        description="Generate runbook snippets from acceptance test evidence"
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        required=True,
        help="Path to evidence directory (e.g., reports/acceptance-full-evidence)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output markdown file path",
    )
    args = parser.parse_args()

    generator = RunbookGenerator(args.evidence_dir)
    report = generator.generate_full_report()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"✅ Runbook snippets generated: {args.output}")


if __name__ == "__main__":
    main()
