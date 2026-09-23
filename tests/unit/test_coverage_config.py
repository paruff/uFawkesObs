"""Tests for test coverage configuration.

Validates that pytest-cov is configured and coverage is measured
for the real source surface (dora/, scripts/).
"""

from __future__ import annotations

import pathlib

import pytest


class TestCoverageConfiguration:
    """Test that coverage is properly configured."""

    def test_pytest_ini_has_cov_config(self):
        """pytest.ini should have --cov configuration."""
        content = pathlib.Path("pytest.ini").read_text()
        assert "--cov" in content or "cov" in content.lower(), (
            "pytest.ini missing --cov configuration"
        )

    def test_pytest_ini_has_cov_source(self):
        """pytest.ini should specify coverage source directories."""
        content = pathlib.Path("pytest.ini").read_text()
        # Should have cov-source for dora/ at minimum
        assert "dora" in content, "pytest.ini missing dora/ in coverage source"

    def test_makefile_test_unit_has_cov(self):
        """Makefile test-unit target should run with coverage."""
        content = pathlib.Path("Makefile").read_text()
        # Find the test-unit target
        in_test_unit = False
        for line in content.splitlines():
            if line.startswith("test-unit:"):
                in_test_unit = True
            elif in_test_unit and line.startswith("## "):
                in_test_unit = False
            elif in_test_unit and "pytest" in line:
                assert "--cov" in line, "Makefile test-unit target missing --cov flag"
                break

    def test_cov_source_includes_dora(self):
        """Coverage should measure dora/ directory (real application code)."""
        content = pathlib.Path("pytest.ini").read_text()
        # Check for cov-source or cov_config that includes dora
        assert "dora" in content, "Coverage source should include dora/ directory"

    def test_cov_source_excludes_test_helpers(self):
        """Coverage should NOT measure tests/acceptance/ helpers.

        From issue #343: "tests/acceptance/ helpers are *not* the target"
        """
        content = pathlib.Path("pytest.ini").read_text()
        # The cov-source should not include tests/acceptance
        # (it's okay if it's mentioned in a comment, but not in --cov=)
        lines = content.splitlines()
        for line in lines:
            if "--cov=" in line and "tests/acceptance" in line:
                pytest.fail("Coverage should not measure tests/acceptance/ helpers")
