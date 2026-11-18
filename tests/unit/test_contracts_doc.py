"""docs/CONTRACTS.md §1 must list every schema property, and mark required ones (DC-01)."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOC = (ROOT / "docs" / "CONTRACTS.md").read_text()
SCHEMAS = sorted((ROOT / "dora" / "events").glob("*-event.schema.json"))


def _table_rows(event_type: str) -> dict[str, str]:
    """Map field name -> 'Required' cell for the §1 table of one event type."""
    section = re.search(
        rf"^#### `{event_type}`.*?(?=^#### |^### |^---)", DOC, re.DOTALL | re.MULTILINE
    )
    assert section, f"CONTRACTS.md has no '#### `{event_type}`' section"
    rows: dict[str, str] = {}
    for line in section.group(0).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and line.startswith("|"):
            for name in re.findall(r"`([a-z_]+)`", cells[0]):
                rows[name] = cells[2]
    return rows


@pytest.mark.parametrize("path", SCHEMAS, ids=lambda p: p.name)
def test_every_schema_property_is_documented(path):
    schema = json.loads(path.read_text())
    rows = _table_rows(path.name.removesuffix("-event.schema.json"))
    missing = set(schema["properties"]) - set(rows)
    assert not missing, (
        f"{path.name}: properties missing from CONTRACTS.md §1: {sorted(missing)}"
    )
    for name in schema["required"]:
        assert rows[name].lower().startswith("yes"), (
            f"{path.name}: {name} must be marked required"
        )
    for name in set(schema["properties"]) - set(schema["required"]):
        assert not rows[name].lower().startswith("yes"), (
            f"{path.name}: {name} is optional"
        )


def test_auth_and_metrics_endpoint_are_documented():
    assert re.search(r"\| `GET`\s+\| `/metrics`", DOC)
    assert "Authorization: Bearer" in DOC
    assert "none is currently enforced" not in DOC
