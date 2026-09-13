"""Tests for README structure and length.

Validates that the README follows the restructured format
targeting ~150 lines for a public landing page.
"""

from __future__ import annotations

import pathlib


class TestReadmeStructure:
    """Test README structure and length constraints."""

    README_PATH = pathlib.Path("README.md")

    def test_readme_exists(self):
        """README.md must exist at repo root."""
        assert self.README_PATH.exists(), "README.md not found at repo root"

    def test_readme_line_count_under_target(self):
        """README should be ~150 lines for a public landing page.

        The issue (#345) targets roughly 150 lines. We allow some buffer
        for badges and necessary content, but anything over 200 suggests
        detail that should be in docs/ was left in.
        """
        content = self.README_PATH.read_text()
        line_count = len(content.splitlines())
        assert line_count <= 200, (
            f"README is {line_count} lines — should be ~150 for a public "
            "landing page. Move detailed content to docs/ files."
        )

    def test_readme_has_what_this_is(self):
        """README must have a 'What This Is' section."""
        content = self.README_PATH.read_text()
        assert "## What This Is" in content or "## What it is" in content.lower(), (
            "README missing 'What This Is' section"
        )

    def test_readme_has_what_this_is_not(self):
        """README must have a 'What This Is Not' section (deliberate positioning).

        This section was deliberately corrected in PR #330 and must not be lost.
        """
        content = self.README_PATH.read_text()
        assert "What This Is Not" in content or "What it is not" in content.lower(), (
            "README missing 'What This Is Not' section — deliberate positioning from PR #330"
        )

    def test_readme_has_quick_start(self):
        """README must have a Quick Start section."""
        content = self.README_PATH.read_text()
        assert "## Quick Start" in content, "README missing Quick Start section"

    def test_readme_has_where_to_go_next(self):
        """README must link to docs/ for further reading."""
        content = self.README_PATH.read_text()
        assert "docs/" in content, "README missing links to docs/"

    def test_readme_has_badges(self):
        """README must have the three badges (CI, License, Part of Fawkes IDP).

        These were explicitly called out to keep in #345.
        """
        content = self.README_PATH.read_text()
        assert "badge.svg" in content or "shields.io" in content, (
            "README missing badges"
        )

    def test_readme_does_not_have_full_port_table(self):
        """Detailed port tables should be in docs/, not README.

        The README should only mention key ports (Grafana, Prometheus)
        in the Quick Start, not the full 18-row table.
        """
        content = self.README_PATH.read_text()
        # Check that the full 18-row port table is not present
        # (the old README had: Grafana, Loki, Tempo, OTel x3, Prometheus,
        # Alertmanager, Tempo gRPC, Loki gRPC, Tempo Zipkin, Alloy,
        # Tempo Jaeger gRPC, Tempo Jaeger HTTP, Telemetry Generator)
        assert "Telemetry Generator" not in content or "5001" not in content, (
            "README has full port table — should only have key ports in Quick Start"
        )

    def test_readme_does_not_have_troubleshooting(self):
        """Troubleshooting should be in docs/, not README.

        The issue explicitly says to move this out.
        """
        content = self.README_PATH.read_text()
        assert "## Troubleshooting" not in content, (
            "README has Troubleshooting section — should be in docs/"
        )
