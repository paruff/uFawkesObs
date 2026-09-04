"""
Unit tests for the DORA regression alert rules (issue #204).

Merges uFawkesDORA's alerts/dora-regression.yaml into
config/prometheus/rules/ufawkesobs-dora-regression.yml, and adds the
pushgateway scrape job these pushed-metric alerts depend on.

Note: uFawkesDORA's alerts/leading-indicator.yaml is deliberately NOT
merged — it references dora_pr_cycle_time_seconds_bucket and
dora_pr_size_lines_added, which nothing in this repo emits yet (no
PR-cycle/PR-size collector exists — that's issue #208 scope).
"""

import pathlib

import yaml


class TestDoraRegressionRulesFile:
    """Test the merged DORA regression alert rules file."""

    def _load(self, project_root):
        rules_path = (
            pathlib.Path(project_root)
            / "config"
            / "prometheus"
            / "rules"
            / "ufawkesobs-dora-regression.yml"
        )
        with open(rules_path, "r") as f:
            return yaml.safe_load(f), rules_path

    def test_rules_file_exists(self, project_root):
        _, path = self._load(project_root)
        assert path.exists(), f"DORA regression rules file not found: {path}"

    def test_rules_file_valid_yaml(self, project_root):
        rules, _ = self._load(project_root)
        assert rules is not None, "DORA regression rules file is empty"

    def test_has_regression_group(self, project_root):
        rules, _ = self._load(project_root)
        group_names = [g["name"] for g in rules["groups"]]
        assert "ufawkesobs_dora_regression" in group_names

    def test_expected_alerts_present(self, project_root):
        rules, _ = self._load(project_root)
        for group in rules["groups"]:
            if group["name"] == "ufawkesobs_dora_regression":
                alert_names = [r["alert"] for r in group["rules"] if "alert" in r]
                required = [
                    "DORARegressionDeploymentFrequencyDrop",
                    "DORARegressionLeadTimeIncrease",
                    "DORARegressionFDRTSpike",
                    "DORARegressionCFRSpike",
                    "DORARegressionReworkRateClimb",
                ]
                for name in required:
                    assert name in alert_names, f"Missing alert: {name}"
                return
        raise AssertionError("ufawkesobs_dora_regression group not found")

    def test_leading_indicator_alerts_not_merged(self, project_root):
        """PR-cycle/PR-size alerts stay out until issue #208 adds a collector."""
        rules, _ = self._load(project_root)
        alert_names = [
            r["alert"]
            for group in rules["groups"]
            for r in group["rules"]
            if "alert" in r
        ]
        assert "DoraLeadingIndicatorPRCycle" not in alert_names
        assert "DoraLeadingIndicatorPRSize" not in alert_names

    def test_alerts_have_category_and_severity(self, project_root):
        rules, _ = self._load(project_root)
        for group in rules["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    labels = rule.get("labels", {})
                    assert "category" in labels, (
                        f"Alert {rule['alert']} missing category label"
                    )
                    assert "severity" in labels, (
                        f"Alert {rule['alert']} missing severity label"
                    )

    def test_alerts_have_runbook_url(self, project_root):
        rules, _ = self._load(project_root)
        for group in rules["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    annotations = rule.get("annotations", {})
                    assert "runbook_url" in annotations, (
                        f"Alert {rule['alert']} missing runbook_url"
                    )
                    assert "paruff/uFawkesObs" in annotations["runbook_url"], (
                        f"Alert {rule['alert']} runbook_url should point at "
                        "uFawkesObs, not the archived uFawkesDORA repo"
                    )

    def test_alerts_reference_pushgateway_metrics(self, project_root):
        """Every expr must reference a metric dora-compute actually emits."""
        rules, _ = self._load(project_root)
        emitted_metrics = {
            "dora_deployment_frequency_per_week",
            "dora_lead_time_p50_hours",
            "dora_lead_time_p95_hours",
            "dora_fdrt_p50_hours",
            "dora_cfr_pct",
            "dora_rework_rate_pct",
        }
        for group in rules["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    expr = rule["expr"]
                    assert any(metric in expr for metric in emitted_metrics), (
                        f"Alert {rule['alert']} expr references no known "
                        f"dora-compute metric: {expr}"
                    )


class TestDoraRegressionRulesReferencedInPrometheusConfig:
    """Test that the new rule file is wired into Prometheus."""

    def test_rule_file_in_rule_files(self, prometheus_config_path):
        with open(prometheus_config_path, "r") as f:
            config = yaml.safe_load(f)

        rule_files = config.get("rule_files", [])
        assert "/etc/prometheus/rules/ufawkesobs-dora-regression.yml" in rule_files, (
            "ufawkesobs-dora-regression.yml should be referenced in rule_files"
        )


class TestDoraApiScrapeJob:
    """Prometheus scrapes dora-api directly for computed DORA metrics.

    Replaces TestPushgatewayScrapeJob (issue #204). Pushgateway is documented
    for ephemeral batch jobs; dora-compute was long-running, so pushing cost
    the `up` liveness signal and left series alive after their producer
    stopped. The compute loop now runs inside dora-api, which exposes
    /metrics for a normal scrape.
    """

    def test_dora_api_job_exists(self, prometheus_config_path):
        with open(prometheus_config_path, "r") as f:
            config = yaml.safe_load(f)

        job_names = [sc["job_name"] for sc in config["scrape_configs"]]
        assert "dora-api" in job_names

    def test_pushgateway_job_removed(self, prometheus_config_path):
        with open(prometheus_config_path, "r") as f:
            config = yaml.safe_load(f)

        job_names = [sc["job_name"] for sc in config["scrape_configs"]]
        assert "pushgateway" not in job_names, (
            "the Pushgateway scrape job was replaced by the dora-api job"
        )

    def test_dora_api_job_does_not_honor_labels(self, prometheus_config_path):
        """honor_labels existed to preserve the pushed job label.

        That label (job="ufawkesdora_<team>") duplicated team_id, which is on
        every sample, and no recording rule or dashboard referenced it. With a
        direct scrape there is nothing to preserve, so honor_labels must stay
        off — leaving it on would let a scraped target overwrite this job's
        own identifying labels.
        """
        with open(prometheus_config_path, "r") as f:
            config = yaml.safe_load(f)

        for sc in config["scrape_configs"]:
            if sc["job_name"] == "dora-api":
                assert sc.get("honor_labels") is not True
                return
        raise AssertionError("dora-api scrape job not found")

    def test_dora_api_job_targets_container(self, prometheus_config_path):
        with open(prometheus_config_path, "r") as f:
            config = yaml.safe_load(f)

        for sc in config["scrape_configs"]:
            if sc["job_name"] == "dora-api":
                targets = sc["static_configs"][0]["targets"]
                assert "dora-api:8088" in targets
                assert sc.get("metrics_path") == "/metrics"
                return
        raise AssertionError("dora-api scrape job not found")
