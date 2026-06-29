"""Evidence collection and report generation for uFawkesObs acceptance tests.

This package provides:
  - EvidenceCollector: Captures test artifacts (payloads, responses, targets)
  - SloReportGenerator: Produces SLO compliance reports from test measurements
  - RunbookSnippetGenerator: Converts test evidence into actionable runbook examples

Each module is importable independently and designed to work with the
ObservabilityStack evidence capture methods.
"""

from tests.acceptance.evidence.slo_report import SloReportGenerator

__all__ = [
    "SloReportGenerator",
]
