"""
Unit tests for the 5 DORA dashboards merged from uFawkesDORA (issue #203).

General Grafana conventions (uid prefix, no numeric datasource IDs,
schemaVersion) are already covered generically for every file under
dashboards/ by tests/unit/test_grafana_dashboards.py. These tests check
the DORA-specific expectations: the 5 dashboards exist with the right
uids, and none of them reference the source repo's placeholder
"PostgreSQL" datasource uid instead of this repo's "ufawkesres-postgres".
"""

from __future__ import annotations

import json
import pathlib

import pytest

DASHBOARDS_DIR = pathlib.Path(__file__).resolve().parents[2] / "dashboards" / "platform"

EXPECTED_DASHBOARDS = {
    "dora-ai-impact.json": "ufawkesobs-dora-ai-impact",
    "dora-archetype-profile.json": "ufawkesobs-dora-archetype-profile",
    "dora-overview.json": "ufawkesobs-dora-overview",
    "dora-leading-indicators.json": "ufawkesobs-dora-leading-indicators",
    "dora-value-stream.json": "ufawkesobs-dora-value-stream",
}


class TestDoraDashboardsMerged:
    @pytest.mark.parametrize(
        "filename,expected_uid",
        EXPECTED_DASHBOARDS.items(),
        ids=list(EXPECTED_DASHBOARDS),
    )
    def test_dashboard_exists_with_expected_uid(self, filename, expected_uid):
        path = DASHBOARDS_DIR / filename
        assert path.exists(), f"Dashboard not found: {path}"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("uid") == expected_uid

    @pytest.mark.parametrize(
        "filename", list(EXPECTED_DASHBOARDS), ids=list(EXPECTED_DASHBOARDS)
    )
    def test_dashboard_uses_repo_postgres_datasource(self, filename):
        """Source dashboards use a placeholder "PostgreSQL" uid — must be
        rewritten to this repo's "ufawkesres-postgres" datasource uid."""
        path = DASHBOARDS_DIR / filename
        raw = path.read_text(encoding="utf-8")
        assert '"PostgreSQL"' not in raw, (
            f"{filename} still references the placeholder PostgreSQL "
            "datasource uid instead of ufawkesres-postgres"
        )

    @pytest.mark.parametrize(
        "filename", list(EXPECTED_DASHBOARDS), ids=list(EXPECTED_DASHBOARDS)
    )
    def test_dashboard_tagged_ufawkesobs(self, filename):
        path = DASHBOARDS_DIR / filename
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert "ufawkesobs" in data.get("tags", [])
