"""
Unit tests that validate Grafana dashboard JSON conventions.

Checks:
  - Top-level uid is present and uses an allowed prefix
  - No numeric datasource IDs (deprecated in Grafana 12.x, removed in 13.x)
  - schemaVersion is present

Run:  pytest tests/unit/test_grafana_dashboards.py -v
      (no running Grafana required — reads JSON files statically)
"""

from __future__ import annotations

import json
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DASHBOARDS_DIR = pathlib.Path(__file__).resolve().parents[2] / "dashboards"

# ---------------------------------------------------------------------------
# Allowed UID prefixes — add new prefixes here, not in test logic
# ---------------------------------------------------------------------------
ALLOWED_UID_PREFIXES = ("ufawkesobs-", "platform-")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _find_dashboard_files() -> list[pathlib.Path]:
    """Recursively find all *.json files under dashboards/."""
    if not DASHBOARDS_DIR.is_dir():
        return []
    return sorted(DASHBOARDS_DIR.rglob("*.json"))


def _load_dashboard(path: pathlib.Path) -> dict:
    """Load and parse a dashboard JSON file."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict), f"{path.name}: top-level JSON must be a mapping"
    return data


def _has_numeric_datasource_id(obj: object, path: str = "") -> list[str]:
    """Recursively find datasource fields that use numeric IDs.

    Grafana 12.x deprecates {"id": N, "type": "..."} datasource refs.
    Grafana 13.x removes them entirely. Use {"uid": "...", "type": "..."} instead.

    Returns a list of paths where numeric datasource IDs were found.
    """
    hits: list[str] = []
    if isinstance(obj, dict):
        # Only check 'datasource' keys — panel "id" fields are fine
        if "datasource" in obj:
            ds = obj["datasource"]
            if isinstance(ds, dict) and "id" in ds and isinstance(ds["id"], (int, float)):
                hits.append(f"{path}.datasource")
        for k, v in obj.items():
            hits.extend(_has_numeric_datasource_id(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            hits.extend(_has_numeric_datasource_id(item, f"{path}[{i}]"))
    return hits


# ---------------------------------------------------------------------------
# Parametrize over discovered dashboard files
# ---------------------------------------------------------------------------
_dashboard_files = _find_dashboard_files()
_dashboard_ids = [str(p.relative_to(DASHBOARDS_DIR)) for p in _dashboard_files]


@pytest.fixture(scope="module")
def dashboards() -> list[tuple[str, dict]]:
    """Load all dashboards as (relative_path, parsed_json) pairs."""
    return [(fid, _load_dashboard(fpath)) for fid, fpath in zip(_dashboard_ids, _dashboard_files)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestGrafanaDashboardConventions:
    """Validate dashboard JSON conventions for Grafana 12.x+ compatibility."""

    @pytest.mark.parametrize("dashboard_id", _dashboard_ids, ids=_dashboard_ids)
    def test_uid_present_and_valid_prefix(
        self, dashboards: list[tuple[str, dict]], dashboard_id: str
    ) -> None:
        """Assert uid exists and starts with an allowed prefix."""
        data = dict(dashboards).get(dashboard_id)
        assert data is not None, f"Dashboard '{dashboard_id}' not loaded"

        uid = data.get("uid")
        assert uid is not None, (
            f"Dashboard '{dashboard_id}' is missing top-level 'uid' field"
        )
        assert isinstance(uid, str) and len(uid) > 0, (
            f"Dashboard '{dashboard_id}' has empty 'uid'"
        )
        assert uid.startswith(ALLOWED_UID_PREFIXES), (
            f"Dashboard '{dashboard_id}' uid '{uid}' does not start with "
            f"an allowed prefix {ALLOWED_UID_PREFIXES}"
        )

    @pytest.mark.parametrize("dashboard_id", _dashboard_ids, ids=_dashboard_ids)
    def test_no_numeric_datasource_id(
        self, dashboards: list[tuple[str, dict]], dashboard_id: str
    ) -> None:
        """Assert no panel or target uses the deprecated numeric datasource ID pattern.

        Grafana 12.x deprecates {"id": N, "type": "..."} datasource refs.
        Grafana 13.x removes them entirely. Use uid-based refs instead.
        """
        data = dict(dashboards).get(dashboard_id)
        assert data is not None, f"Dashboard '{dashboard_id}' not loaded"

        hits = _has_numeric_datasource_id(data)
        assert not hits, (
            f"Dashboard '{dashboard_id}' contains {len(hits)} numeric datasource ID "
            f"reference(s) at: {', '.join(hits[:5])}. "
            f"Replace with uid-based datasource references."
        )

    @pytest.mark.parametrize("dashboard_id", _dashboard_ids, ids=_dashboard_ids)
    def test_schema_version_present(
        self, dashboards: list[tuple[str, dict]], dashboard_id: str
    ) -> None:
        """Assert schemaVersion is present in the dashboard JSON."""
        data = dict(dashboards).get(dashboard_id)
        assert data is not None, f"Dashboard '{dashboard_id}' not loaded"

        sv = data.get("schemaVersion")
        assert sv is not None, (
            f"Dashboard '{dashboard_id}' is missing 'schemaVersion' field"
        )
        assert isinstance(sv, (int, float)), (
            f"Dashboard '{dashboard_id}' schemaVersion must be a number, "
            f"got {type(sv).__name__}"
        )

    def test_dashboards_directory_graceful_skip(self) -> None:
        """If dashboards/ has no JSON files, report 0 collected (not error)."""
        count = len(_dashboard_files)
        # This test always passes — it documents the graceful-skip behavior.
        # The parametrized tests above will have 0 items if no files exist.
        assert count >= 0, "Sanity check: count cannot be negative"
