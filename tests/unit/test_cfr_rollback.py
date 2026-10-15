"""CFR-triggered rollback wiring (#502).

Behaviour (alert detection, rollback, idempotence) is covered end to end by
tests/acceptance/features/cfr_rollback.feature; these check the glue.
"""

import json
import pathlib
import subprocess

import yaml


def test_alert_script_fails_when_prometheus_unreachable(project_root):
    # An unreadable alert state must never be read as "all clear".
    r = subprocess.run(
        [f"{project_root}/scripts/cfr-alert-firing.sh", "http://127.0.0.1:1"],
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0


def test_workflow_is_gated_and_wired_to_scripts(project_root):
    root = pathlib.Path(project_root)
    wf = yaml.safe_load((root / ".github/workflows/cfr-rollback.yml").read_text())
    job = wf["jobs"]["rollback"]
    assert "CFR_AUTO_ROLLBACK_ENABLED" in job["if"]
    steps = json.dumps(job["steps"])
    assert "cfr-alert-firing.sh" in steps and "rollback-latest-good.sh" in steps
    assert (
        "DORACFRRegressionRollback"
        in (root / "scripts/cfr-alert-firing.sh").read_text()
    )


def test_rules_file_registered_in_prometheus_config(project_root):
    cfg = yaml.safe_load(
        pathlib.Path(project_root, "config/prometheus/prometheus.yaml").read_text()
    )
    assert "/etc/prometheus/rules/ufawkesobs-slo-burn-rate.yml" in cfg["rule_files"]
