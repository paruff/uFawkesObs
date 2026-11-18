"""DORA alert text, the threshold table and dashboard datasources match the rules (DC-06, DC-07)."""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
RULES = yaml.safe_load(
    (ROOT / "config/prometheus/rules/ufawkesobs-dora-metrics.yml").read_text()
)
ALERTS = {
    r["alert"]: r
    for g in RULES["groups"]
    for r in g["rules"]
    if "alert" in r and "Absent" not in r["alert"]
}
PROVISIONED = {
    ds["uid"]
    for ds in yaml.safe_load(
        (ROOT / "config/grafana/provisioning/datasources/datasources.yaml").read_text()
    )["datasources"]
}


def _panels(items):
    for p in items:
        yield p
        yield from _panels(p.get("panels", []))


def _threshold(rule) -> str:
    return re.search(r"[<>]\s*([0-9.]+)", rule["expr"]).group(1)


def test_frequency_alert_says_per_week_because_the_expression_is_per_week():
    rule = ALERTS["DORADeploymentFrequencyLow"]
    assert "per_week" in rule["expr"] or "deployment_frequency" in rule["expr"]
    assert "per week" in rule["annotations"]["summary"]
    assert "30 days" not in rule["annotations"]["summary"]


def test_threshold_table_matches_every_rule():
    overview = json.loads((ROOT / "dashboards/platform/dora-overview.json").read_text())
    panel = next(
        p for p in _panels(overview["panels"]) if p["title"] == "DORA Alert Thresholds"
    )
    text = panel["options"]["content"]
    for name, rule in ALERTS.items():
        assert name in text, f"threshold table lacks {name}"
        row = next(line for line in text.splitlines() if name in line)
        assert _threshold(rule) in row, (
            f"{name}: table row disagrees with expr {rule['expr']!r}"
        )


def test_no_dora_panel_uses_an_unprovisioned_datasource():
    for path in (ROOT / "dashboards/platform").glob("dora-*.json"):
        for p in _panels(json.loads(path.read_text())["panels"]):
            uid = (p.get("datasource") or {}).get("uid")
            assert uid is None or uid in PROVISIONED, (
                f"{path.name}: panel {p['title']!r} uses {uid!r}"
            )
            assert "rawSql" not in json.dumps(p), (
                f"{path.name}: panel {p['title']!r} has a SQL query"
            )
