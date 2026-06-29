"""
SLO Compliance Report Generator.

Produces structured markdown and JSON reports from SLO measurements
collected during acceptance test runs. The report is consumed by:
  - CI/CD pipeline for compliance dashboards
  - Weekly platform review
  - Runbook generation (Phase 6)

Usage:
    from tests.acceptance.steps.slo_steps import get_slo_results
    from tests.acceptance.evidence.slo_report import SloReportGenerator

    report = SloReportGenerator(get_slo_results())
    report.save_markdown("reports/slo-report.md")
    report.save_json("reports/slo-report.json")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SloResult:
    """A single SLO measurement result for reporting."""

    sli_id: str
    sli_name: str
    measured_ms: float
    slo_threshold_ms: float
    passed: bool
    extra: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SloReportGenerator:
    """Generates structured SLO compliance reports from measurements.

    Takes a list of SLO measurement results and produces:
      - Markdown report with histogram-style latency summary
      - JSON report for programmatic consumption
      - Overall pass/fail summary
    """

    def __init__(self, results: list[dict[str, Any]] | None = None):
        """Initialise the report generator.

        Args:
            results: List of SLO measurement dicts, typically from
                     steps.slo_steps.get_slo_results(). Each dict should
                     contain: sli_id, sli_name, measured_ms, slo_threshold_ms,
                     passed, extra, timestamp.
        """
        self.results: list[SloResult] = []
        if results:
            for r in results:
                if isinstance(r, dict):
                    self.results.append(SloResult(**r))
                elif isinstance(r, SloResult):
                    self.results.append(r)

        self.generated_at = datetime.now(timezone.utc)

    def add_result(self, result: SloResult | dict[str, Any]) -> None:
        """Add a single SLO result to the report."""
        if isinstance(result, dict):
            self.results.append(SloResult(**result))
        else:
            self.results.append(result)

    # ── Properties ────────────────────────────────────────────────────

    @property
    def passed_count(self) -> int:
        """Number of SLO measurements that passed."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        """Number of SLO measurements that failed."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def total_count(self) -> int:
        """Total number of SLO measurements."""
        return len(self.results)

    @property
    def overall_passed(self) -> bool:
        """True if all SLO measurements passed."""
        return self.failed_count == 0 and self.total_count > 0

    @property
    def pass_rate(self) -> float:
        """Fraction of SLO measurements that passed (0.0 - 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.passed_count / self.total_count

    # ── Latency-specific results ──────────────────────────────────────

    @property
    def latency_results(self) -> list[SloResult]:
        """Return only latency-based SLO results (excluding scrape/datasource/dashboard)."""
        return [
            r
            for r in self.results
            if r.sli_id in ("OBS-SLI-001", "OBS-SLI-002", "OBS-SLI-003")
        ]

    # ── Report Generation ─────────────────────────────────────────────

    def generate_markdown(self) -> str:
        """Generate a markdown SLO compliance report."""
        lines: list[str] = []

        lines.append("# SLO Compliance Report\n")
        lines.append(
            f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        )
        lines.append(
            f"**Overall Status:** {'✅ PASS' if self.overall_passed else '❌ FAIL'}\n"
        )
        lines.append(
            f"**Pass Rate:** {self.passed_count}/{self.total_count} "
            f"({self.pass_rate * 100:.1f}%)\n"
        )

        lines.append("---\n")

        # Summary table
        lines.append("## Summary\n")
        lines.append("| SLI ID | SLI Name | Measured | SLO Threshold | Status |")
        lines.append("|--------|----------|----------|---------------|--------|")
        for r in self.results:
            measured = (
                f"{r.measured_ms:.0f}ms" if r.slo_threshold_ms > 0 else "N/A (binary)"
            )
            threshold = (
                f"<{r.slo_threshold_ms:.0f}ms"
                if r.slo_threshold_ms > 0
                else "N/A (binary)"
            )
            status = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(
                f"| {r.sli_id} | {r.sli_name} | {measured} | {threshold} | {status} |"
            )

        # Latency details
        latency_results = self.latency_results
        if latency_results:
            lines.append("\n## Ingestion Latency Details\n")
            for r in latency_results:
                excess = r.measured_ms - r.slo_threshold_ms
                lines.append(f"### {r.sli_id}: {r.sli_name}\n")
                lines.append(f"- **Measured:** {r.measured_ms:.0f}ms")
                lines.append(f"- **SLO Target:** <{r.slo_threshold_ms:.0f}ms")
                if r.passed:
                    margin = r.slo_threshold_ms - r.measured_ms
                    lines.append(f"- **Margin:** {margin:.0f}ms under SLO ✅")
                else:
                    lines.append(f"- **Excess:** +{excess:.0f}ms over SLO ❌")
                lines.append("")

        # Non-latency details
        non_latency = [r for r in self.results if r not in latency_results]
        if non_latency:
            lines.append("## Binary SLO Results\n")
            for r in non_latency:
                status = "✅ PASS" if r.passed else "❌ FAIL"
                lines.append(f"### {r.sli_id}: {r.sli_name} — {status}\n")
                for key, value in r.extra.items():
                    if key in ("target_status", "details"):
                        lines.append(f"- **{key}:** (see JSON report for full details)")
                    else:
                        lines.append(f"- **{key}:** {value}")
                lines.append("")

        # Violations section
        if self.failed_count > 0:
            lines.append("## SLO Violations\n")
            lines.append(
                "The following SLO targets were not met and require investigation:\n"
            )
            for r in self.results:
                if not r.passed:
                    measured = (
                        f"{r.measured_ms:.0f}ms" if r.slo_threshold_ms > 0 else "N/A"
                    )
                    threshold = (
                        f"<{r.slo_threshold_ms:.0f}ms"
                        if r.slo_threshold_ms > 0
                        else "N/A"
                    )
                    lines.append(
                        f"- **{r.sli_id}** ({r.sli_name}): "
                        f"Measured {measured}, SLO {threshold}"
                    )
            lines.append("")

        lines.append("---\n")
        lines.append(
            f"*Report generated by uFawkesAI SLO Test Gate "
            f"({self.generated_at.isoformat()})*"
        )

        return "\n".join(lines)

    def generate_json(self) -> dict[str, Any]:
        """Generate a JSON-serialisable SLO compliance report."""
        return {
            "report_type": "slo_compliance",
            "generated_at": self.generated_at.isoformat(),
            "overall_passed": self.overall_passed,
            "pass_rate": round(self.pass_rate, 4),
            "summary": {
                "total": self.total_count,
                "passed": self.passed_count,
                "failed": self.failed_count,
            },
            "results": [asdict(r) for r in self.results],
        }

    # ── Output ────────────────────────────────────────────────────────

    def save_markdown(self, path: str | Path) -> Path:
        """Save the markdown report to a file.

        Args:
            path: File path for the markdown report.

        Returns:
            Path to the saved file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_markdown())
        print(f"📄 SLO report saved: {path}")
        return path

    def save_json(self, path: str | Path) -> Path:
        """Save the JSON report to a file.

        Args:
            path: File path for the JSON report.

        Returns:
            Path to the saved file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.generate_json(), indent=2, default=str))
        print(f"📄 SLO JSON report saved: {path}")
        return path

    def save_both(self, base_path: str | Path) -> tuple[Path, Path]:
        """Save both markdown and JSON reports.

        Args:
            base_path: Base path (without extension). Reports are saved as
                       {base_path}.md and {base_path}.json.

        Returns:
            (markdown_path, json_path)
        """
        base = Path(base_path)
        md = self.save_markdown(base.with_suffix(".md"))
        js = self.save_json(base.with_suffix(".json"))
        return md, js


# ── CLI Entry Point ───────────────────────────────────────────────────
#
# Usage:
#   python -m tests.acceptance.evidence.slo_report \
#     --evidence-dir reports/acceptance-full-evidence \
#     --output reports/slo-report.md

if __name__ == "__main__":
    import argparse
    import sys

    # Add repo root to path for imports when run as script
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))

    parser = argparse.ArgumentParser(
        description="Generate SLO compliance report from test evidence"
    )
    parser.add_argument(
        "--evidence-dir",
        type=str,
        required=True,
        help="Directory containing SLO evidence JSON files",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/slo-report.md",
        help="Output path for the markdown report (default: reports/slo-report.md)",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Output path for JSON report (default: derived from --output)",
    )
    args = parser.parse_args()

    evidence_dir = Path(args.evidence_dir)
    if not evidence_dir.exists():
        print(f"❌ Evidence directory not found: {evidence_dir}")
        sys.exit(1)

    # Load all SLO evidence JSON files
    results: list[dict[str, Any]] = []
    for evidence_file in sorted(evidence_dir.glob("*.json")):
        try:
            data = json.loads(evidence_file.read_text())
            artifacts = data.get("artifacts", {})
            slo_data = artifacts.get("slo_measurements", [])
            results.extend(slo_data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Skipping {evidence_file.name}: {e}")

    if not results:
        print("⚠️  No SLO measurements found in evidence directory")
        sys.exit(0)

    report = SloReportGenerator(results)
    output_path = Path(args.output)
    json_path = (
        Path(args.json_output)
        if args.json_output
        else (
            output_path.with_suffix(".json")
            if output_path.suffix == ".md"
            else output_path.parent / f"{output_path.stem}.json"
        )
    )

    report.save_markdown(output_path)
    report.save_json(json_path)

    print(f"\n{'=' * 60}")
    print("SLO Report Summary:")
    print(f"  Total:    {report.total_count}")
    print(f"  Passed:   {report.passed_count}")
    print(f"  Failed:   {report.failed_count}")
    print(f"  Pass Rate: {report.pass_rate * 100:.1f}%")
    print(f"  Overall:  {'✅ PASS' if report.overall_passed else '❌ FAIL'}")
    print(f"{'=' * 60}")
