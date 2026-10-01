"""
Unit tests for DORA recording + alert rules (issue #533).

The recording rules carry an `or vector(0)` fallback so dashboards never
see gaps — but that makes the series perpetually present, which broke
two things:

  * every paired ``absent()`` guard was dead code (never fires), and
  * ``DORADeploymentFrequencyLow`` read "no data flowing" as "zero
    deployments" and paged stacks that simply don't run the DORA
    pipeline.

Fix shape under test: raw (fallback-less) recording rules feed the
absent() guards and the Low alert; the fallback rules remain for
dashboards and the threshold alerts where 0 can never cross them.
"""

import pathlib
from urllib.parse import urlparse

import yaml

RAW_RECORDINGS = {
    "dora:deployment_frequency:raw30d": "dora:deployment_frequency:rate30d",
    "dora:lead_time_hours:raw_p50_30d": "dora:lead_time_hours:p50_30d",
    "dora:change_failure_rate:raw_ratio30d": ("dora:change_failure_rate:ratio30d"),
    "dora:fdrt_hours:raw_p50_30d": "dora:fdrt_hours:p50_30d",
    "dora:rework_rate:raw_ratio": "dora:rework_rate:ratio",
}

ABSENT_ALERT_TARGETS = {
    "DORADeploymentFrequencyLowAbsent": "dora:deployment_frequency:raw30d",
    "DORALeadTimeHighAbsent": "dora:lead_time_hours:raw_p50_30d",
    "DORAChangeFailureRateHighAbsent": ("dora:change_failure_rate:raw_ratio30d"),
    "DORAFDRTHighAbsent": "dora:fdrt_hours:raw_p50_30d",
    "DORAReworkRateHighAbsent": "dora:rework_rate:raw_ratio",
}


def _load_rules(project_root):
    rules_path = (
        pathlib.Path(project_root)
        / "config"
        / "prometheus"
        / "rules"
        / "ufawkesobs-dora-metrics.yml"
    )
    with open(rules_path, "r") as f:
        return yaml.safe_load(f)


def _load_all_dora_rules(project_root):
    repo_root = pathlib.Path(project_root)
    alert_map = {}
    for filename in [
        "ufawkesobs-dora-metrics.yml",
        "ufawkesobs-dora-regression.yml",
    ]:
        rules_path = repo_root / "config" / "prometheus" / "rules" / filename
        with open(rules_path, "r") as f:
            rules = yaml.safe_load(f)
        for group in rules["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    alert_map[rule["alert"]] = rule
    return alert_map


def _by_kind(rules, key):
    return {
        rule[key]: rule
        for group in rules["groups"]
        for rule in group["rules"]
        if key in rule
    }


_EXPECTED_RUNBOOK_TARGETS = {
    "DORADeploymentFrequencyLow": "#deployment-frequency-low",
    "DORADeploymentFrequencyLowAbsent": "#deployment-frequency-absent",
    "DORALeadTimeHigh": "#lead-time-high",
    "DORALeadTimeHighAbsent": "#lead-time-absent",
    "DORAChangeFailureRateHigh": "#change-failure-rate-high",
    "DORAChangeFailureRateCritical": "#change-failure-rate-critical",
    "DORAChangeFailureRateHighAbsent": "#change-failure-rate-absent",
    "DORAFDRTHigh": "#fdrt-high",
    "DORAFDRTHighAbsent": "#fdrt-absent",
    "DORAReworkRateHigh": "#rework-rate-high",
    "DORAReworkRateCritical": "#rework-rate-critical",
    "DORAReworkRateHighAbsent": "#rework-rate-absent",
    "DORARegressionDeploymentFrequencyDrop": "#deployment-frequency-drop",
    "DORARegressionDeploymentFrequencyDropAbsent": "#deployment-frequency-drop-absent",
    "DORARegressionLeadTimeIncrease": "#lead-time-increase",
    "DORARegressionLeadTimeIncreaseAbsent": "#lead-time-increase-absent",
    "DORARegressionFDRTSpike": "#fdrt-spike",
    "DORARegressionFDRTSpikeAbsent": "#fdrt-spike-absent",
    "DORARegressionCFRSpike": "#cfr-spike",
    "DORARegressionCFRSpikeAbsent": "#cfr-spike-absent",
    "DORARegressionReworkRateClimb": "#rework-rate-climb",
    "DORARegressionReworkRateClimbAbsent": "#rework-rate-climb-absent",
}


class TestRawRecordingRules:
    """Raw rules are the presence-aware series alert guards rely on."""

    def test_raw_rules_exist_for_all_five_metrics(self, project_root):
        records = _by_kind(_load_rules(project_root), "record")
        for raw_name in RAW_RECORDINGS:
            assert raw_name in records, (
                f"Missing raw recording rule {raw_name} — absent() guards "
                "and DORADeploymentFrequencyLow need a series that can "
                "actually disappear"
            )

    def test_raw_rules_have_no_vector_fallback(self, project_root):
        records = _by_kind(_load_rules(project_root), "record")
        for raw_name in RAW_RECORDINGS:
            assert raw_name in records, f"Missing raw rule: {raw_name}"
            assert "vector(0)" not in records[raw_name]["expr"], (
                f"{raw_name} must not carry the vector(0) fallback or it "
                "can never be absent"
            )

    def test_fallback_rules_still_exist_for_dashboards(self, project_root):
        """Dashboards keep the gap-free series; this change must not drop it."""
        records = _by_kind(_load_rules(project_root), "record")
        for fallback_name in RAW_RECORDINGS.values():
            assert fallback_name in records, (
                f"Missing fallback rule {fallback_name} — dashboards read it"
            )
            assert "vector(0)" in records[fallback_name]["expr"], (
                f"{fallback_name} should keep the vector(0) fallback"
            )


class TestAbsentGuardsCanFire:
    """absent() must target a series that disappears with the data."""

    def test_absent_alerts_target_raw_series(self, project_root):
        alerts = _by_kind(_load_rules(project_root), "alert")
        for alert_name, raw_target in ABSENT_ALERT_TARGETS.items():
            assert alert_name in alerts, f"Missing alert: {alert_name}"
            expr = alerts[alert_name]["expr"]
            assert f"absent({raw_target})" == expr.strip(), (
                f"{alert_name} must be absent({raw_target}); got: {expr.strip()}"
            )

    def test_absent_alerts_never_target_fallback_series(self, project_root):
        alerts = _by_kind(_load_rules(project_root), "alert")
        fallback_names = list(RAW_RECORDINGS.values())
        for alert_name in ABSENT_ALERT_TARGETS:
            expr = alerts[alert_name]["expr"]
            for fallback in fallback_names:
                assert fallback not in expr, (
                    f"{alert_name} targets fallback rule {fallback}, which "
                    "always exists — the guard can never fire"
                )

    def test_absent_alerts_fire_within_one_day(self, project_root):
        """7d of missing DORA data made the guards effectively undetectable."""
        alerts = _by_kind(_load_rules(project_root), "alert")
        for alert_name in ABSENT_ALERT_TARGETS:
            assert alerts[alert_name].get("for") == "1d", (
                f"{alert_name} should fire after 1d of missing data, got "
                f"for={alerts[alert_name].get('for')!r}"
            )


class TestDeploymentFrequencyLowGuards:
    """Low must page only on real low-frequency data, never on missing data."""

    def test_low_alert_evaluates_raw_series(self, project_root):
        alerts = _by_kind(_load_rules(project_root), "alert")
        expr = alerts["DORADeploymentFrequencyLow"]["expr"]
        assert "dora:deployment_frequency:raw30d" in expr, (
            "DORADeploymentFrequencyLow must evaluate the raw series so a "
            f"stack with no DORA data cannot page; got: {expr.strip()}"
        )

    def test_low_alert_does_not_use_fallback_series(self, project_root):
        alerts = _by_kind(_load_rules(project_root), "alert")
        expr = alerts["DORADeploymentFrequencyLow"]["expr"]
        assert "dora:deployment_frequency:rate30d" not in expr, (
            "the fallback series is 0 when data is missing — using it makes "
            "no-data stacks look like zero-deployment stacks"
        )


class TestAlertConventionsKept:
    """The file's existing conventions survive the change."""

    def test_all_alerts_have_required_labels_and_runbook(self, project_root):
        alerts = _by_kind(_load_rules(project_root), "alert")
        for name, rule in alerts.items():
            labels = rule.get("labels", {})
            assert "severity" in labels, f"{name} missing severity"
            assert labels.get("category") == "dora", f"{name} missing category"
            annotations = rule.get("annotations", {})
            assert "runbook_url" in annotations, f"{name} missing runbook_url"
            assert "summary" in annotations, f"{name} missing summary"

    def test_all_runbook_urls_resolve_to_existing_files_and_anchors(self, project_root):
        alerts = _load_all_dora_rules(project_root)
        repo_root = pathlib.Path(project_root)
        runbook_path = repo_root / "docs" / "runbooks" / "dora.md"
        assert runbook_path.exists(), f"Missing runbook file: {runbook_path}"
        runbook_text = runbook_path.read_text(encoding="utf-8")

        for name in _EXPECTED_RUNBOOK_TARGETS:
            assert name in alerts, (
                f"{name} in _EXPECTED_RUNBOOK_TARGETS but missing from DORA rule files"
            )

        for name, rule in alerts.items():
            annotations = rule.get("annotations", {})
            url = annotations.get("runbook_url")
            assert url is not None, f"{name} missing runbook_url"
            parsed = urlparse(url)
            assert parsed.scheme == "https", (
                f"{name} runbook_url should be HTTPS: {url}"
            )
            assert parsed.netloc == "github.com", (
                f"{name} runbook_url should point to github.com: {url}"
            )
            assert parsed.path.startswith("/paruff/uFawkesObs/"), (
                f"{name} runbook_url should point to the uFawkesObs repo: {url}"
            )
            assert parsed.path.endswith("/docs/runbooks/dora.md"), (
                f"{name} runbook_url should target docs/runbooks/dora.md: {url}"
            )

            expected_anchor = _EXPECTED_RUNBOOK_TARGETS.get(name)
            assert expected_anchor is not None, (
                f"{name} not in _EXPECTED_RUNBOOK_TARGETS — add its runbook anchor"
            )
            fragment = expected_anchor.lstrip("#")
            assert parsed.fragment == fragment, (
                f"{name} should target anchor {fragment}, got {parsed.fragment!r}"
            )
            assert f'<a id="{parsed.fragment}"></a>' in runbook_text, (
                f"{name} anchor id {parsed.fragment} missing in {runbook_path}"
            )

    def test_rule_file_wired_into_prometheus(self, project_root):
        config_path = (
            pathlib.Path(project_root) / "config" / "prometheus" / "prometheus.yaml"
        )
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        assert "/etc/prometheus/rules/ufawkesobs-dora-metrics.yml" in config.get(
            "rule_files", []
        )
