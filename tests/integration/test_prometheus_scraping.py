"""
Integration tests for Prometheus metric scraping.
Tests that Prometheus scrapes all configured targets correctly.

Migrated to Testcontainers (#416): `test_all_configured_targets_are_up`
asserts every job in config/prometheus/prometheus.yaml except dora-api is
up, which means this file genuinely needs the whole `core` profile running
-- not a subset. Provisions it per test-module run instead of assuming
`make up` already started a shared stack.

Feature: Prometheus Metric Scraping
  As a DevOps engineer
  I want Prometheus to scrape all configured targets
  So that metrics are collected reliably
"""

from __future__ import annotations

import os
import pathlib
import tempfile
import time
from typing import Any

import pytest
import requests
from testcontainers.compose import DockerCompose

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRAPE_SLA_SECONDS = 1.0  # Scrape should complete in under 1 second
GRAFANA_ADMIN_PASSWORD = os.environ.get("GRAFANA_ADMIN_PASSWORD", "admin")


@pytest.fixture(scope="module")
def prometheus_stack():
    # This provisions the whole `core` profile (grafana included), which
    # compose.yaml requires GRAFANA_ADMIN_PASSWORD for. docker compose
    # auto-loads this repo's own .env ahead of this process's environment
    # (confirmed live in #416/Grafana's migration) -- an explicit env_file
    # is the override that actually takes precedence.
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
        f.write(f"GRAFANA_ADMIN_PASSWORD={GRAFANA_ADMIN_PASSWORD}\n")
        # compose.yaml's alertmanager secret (`environment: SLACK_WEBHOOK_URL`)
        # must exist (even empty) or `docker compose up` on the whole
        # profile (no explicit services=) refuses to start anything --
        # matches ci-tests.yml's own job-level env var for the same reason.
        f.write(f"SLACK_WEBHOOK_URL={os.environ.get('SLACK_WEBHOOK_URL', '')}\n")
        env_file_path = f.name

    try:
        with DockerCompose(
            context=str(REPO_ROOT),
            compose_file_name="compose.yaml",
            env_file=env_file_path,
            profiles=["core"],
            wait=True,
        ) as compose:
            yield compose
    finally:
        os.unlink(env_file_path)


@pytest.fixture(scope="module")
def prometheus_url(prometheus_stack: DockerCompose) -> str:
    host, port = prometheus_stack.get_service_host_and_port("prometheus", 9090)
    url = f"http://{host}:{int(port)}"

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{url}/-/ready", timeout=5).status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        pytest.fail("Prometheus did not report /-/ready within 60s")

    # Replaces the original file's blind `time.sleep(10)` ("give Prometheus
    # a bit more time to start scraping") -- poll until every core job
    # (test_all_configured_targets_are_up's own list) shows up=1, not just
    # otel-collector. Grafana in particular has a 60s healthcheck
    # start_period, so it's routinely still "down" on the first scrape
    # attempt or two even after Prometheus itself is ready.
    expected_up_jobs = {
        "prometheus",
        "otel-collector",
        "otel-app-metrics",
        "alertmanager",
        "alloy",
        "loki",
        "tempo",
        "grafana",
        "node-exporter",
    }
    up_jobs: set[str] = set()
    healthy_jobs: set[str] = set()
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            data = query_prometheus(url, "up")
            up_jobs = {
                r["metric"].get("job")
                for r in data.get("result", [])
                if float(r.get("value", [0, "0"])[1]) == 1.0
            }
            # /api/v1/targets' own health field can lag a scrape or two
            # behind the `up` metric -- wait for both to agree, since
            # test_get_all_targets_details asserts on this endpoint too.
            healthy_jobs = {
                t["labels"].get("job")
                for t in get_targets(url)
                if t.get("health") == "up"
            }
            if expected_up_jobs.issubset(up_jobs & healthy_jobs):
                return url
        except (requests.exceptions.RequestException, ValueError, KeyError):
            pass
        time.sleep(2)
    pytest.fail(
        f"Prometheus never scraped all core jobs as up within 90s "
        f"(missing from up metric: {expected_up_jobs - up_jobs}, "
        f"missing from /targets health: {expected_up_jobs - healthy_jobs})"
    )


def query_prometheus(prometheus_url: str, query: str) -> dict[str, Any]:
    response = requests.get(
        f"{prometheus_url}/api/v1/query", params={"query": query}, timeout=10
    )
    response.raise_for_status()
    result = response.json()

    if result.get("status") != "success":
        raise ValueError(f"Query failed: {result.get('error', 'Unknown error')}")

    return result.get("data", {})


def get_targets(prometheus_url: str) -> list[dict[str, Any]]:
    response = requests.get(f"{prometheus_url}/api/v1/targets", timeout=10)
    response.raise_for_status()
    result = response.json()

    if result.get("status") != "success":
        raise ValueError(
            f"Failed to get targets: {result.get('error', 'Unknown error')}"
        )

    return result.get("data", {}).get("activeTargets", [])


class TestPrometheusOTelCollectorScraping:
    """Test Prometheus scraping of OTel Collector metrics."""

    def test_otel_collector_target_is_up(self, prometheus_url: str):
        """
        Scenario: Prometheus scrapes OTel Collector successfully
          Given Obstackd stack is running
          And OTel Collector is exporting metrics on port 8888
          When I query Prometheus for 'up{job="otel-collector"}'
          Then the result should show value=1
        """
        data = query_prometheus(prometheus_url, 'up{job="otel-collector"}')

        results = data.get("result", [])
        assert len(results) > 0, "OTel Collector target should exist in Prometheus"

        up_value = float(results[0].get("value", [0, "0"])[1])
        assert up_value == 1.0, f"OTel Collector should be up (value=1), got {up_value}"

    def test_otel_collector_scrape_duration(self, prometheus_url: str):
        """Test that OTel Collector scrape completes in under 1 second."""
        data = query_prometheus(
            prometheus_url, 'scrape_duration_seconds{job="otel-collector"}'
        )

        results = data.get("result", [])
        assert len(results) > 0, "Scrape duration metric should exist"

        duration = float(results[0].get("value", [0, "0"])[1])
        assert duration < SCRAPE_SLA_SECONDS, (
            f"Scrape duration should be < {SCRAPE_SLA_SECONDS}s, got {duration}s"
        )

    def test_otel_collector_no_scrape_errors(self, prometheus_url: str):
        """Test that there are no scrape errors for OTel Collector."""
        data = query_prometheus(prometheus_url, 'up{job="otel-collector"}')

        results = data.get("result", [])
        for result in results:
            up_value = float(result.get("value", [0, "0"])[1])
            if up_value != 1.0:
                instance = result.get("metric", {}).get("instance", "unknown")
                pytest.fail(f"Scrape error detected for instance {instance}")

    def test_otel_collector_metrics_available(self, prometheus_url: str):
        """Test that OTel Collector is exporting expected metrics."""
        expected_metrics = [
            "otelcol_process_uptime",
            "otelcol_receiver_accepted_spans",
            "otelcol_receiver_accepted_metric_points",
            "otelcol_exporter_sent_spans",
            "otelcol_exporter_sent_metric_points",
        ]

        for metric in expected_metrics:
            # Some metrics might not have data yet if no traffic has been
            # sent -- we just check that the query itself succeeds.
            query_prometheus(prometheus_url, metric)


class TestPrometheusAllTargets:
    """Test that all configured Prometheus targets are healthy."""

    def test_all_configured_targets_are_up(self, prometheus_url: str):
        """
        Scenario: All configured targets are healthy
          Given Obstackd stack is running
          When I query Prometheus for all 'up' metrics
          Then all core targets should have value=1
        """
        data = query_prometheus(prometheus_url, "up")

        results = data.get("result", [])
        assert len(results) > 0, "Should have at least one target configured"

        # dora-api is dora-profile-only; this file provisions --profile
        # core only, so it's never started here.
        optional_services = ["dora-api"]

        down_core_targets = []
        down_optional_targets = []

        for result in results:
            metric = result.get("metric", {})
            job = metric.get("job", "unknown")
            instance = metric.get("instance", "unknown")
            up_value = float(result.get("value", [0, "0"])[1])

            if up_value != 1.0:
                if job in optional_services:
                    down_optional_targets.append(f"{job}/{instance}")
                else:
                    down_core_targets.append(f"{job}/{instance}")

        assert len(down_core_targets) == 0, (
            f"Core targets should be up, but these are down: {', '.join(down_core_targets)}"
        )

    def test_no_targets_with_zero_samples(self, prometheus_url: str):
        """
        Scenario: All configured targets are healthy
          And no core scrape_samples_scraped should be 0
        """
        data = query_prometheus(prometheus_url, 'scrape_samples_scraped{job!=""} == 0')

        results = data.get("result", [])

        # otel-app-metrics only has samples when applications send OTLP
        # telemetry; dora-api is dora-profile-only (not started here).
        optional_services = ["otel-app-metrics", "dora-api"]

        core_zero_sample_targets = [
            f"{r.get('metric', {}).get('job', 'unknown')}/{r.get('metric', {}).get('instance', 'unknown')}"
            for r in results
            if r.get("metric", {}).get("job", "unknown") not in optional_services
        ]

        assert not core_zero_sample_targets, (
            f"Core targets are not producing samples: {', '.join(core_zero_sample_targets)}"
        )

    def test_all_targets_scrape_duration_within_sla(self, prometheus_url: str):
        """Test that all target scrapes complete within SLA."""
        data = query_prometheus(
            prometheus_url, f"scrape_duration_seconds > {SCRAPE_SLA_SECONDS}"
        )

        results = data.get("result", [])
        slow_targets = [
            f"{r.get('metric', {}).get('job', 'unknown')}/{r.get('metric', {}).get('instance', 'unknown')} "
            f"({float(r.get('value', [0, '0'])[1]):.3f}s)"
            for r in results
        ]

        assert not slow_targets, (
            f"These targets exceed scrape SLA ({SCRAPE_SLA_SECONDS}s): {', '.join(slow_targets)}"
        )


class TestPrometheusMetricLabels:
    """Test that metrics have correct labels."""

    def test_otel_receiver_metrics_have_required_labels(self, prometheus_url: str):
        """
        Scenario: Metrics have correct labels
          Given Prometheus is scraping metrics
          When I query for 'otelcol_receiver_accepted_spans'
          Then the metric should have required labels
        """
        data = query_prometheus(prometheus_url, "otelcol_receiver_accepted_spans")

        results = data.get("result", [])
        if len(results) > 0:
            metric = results[0].get("metric", {})
            expected_labels = ["job", "instance", "receiver", "transport"]

            for label in expected_labels:
                assert label in metric, (
                    f"Metric should have label '{label}', got labels: {list(metric.keys())}"
                )

    def test_metrics_have_job_label(self, prometheus_url: str):
        """Test that all metrics have a 'job' label."""
        data = query_prometheus(prometheus_url, 'up{job=""}')

        results = data.get("result", [])
        assert len(results) == 0, (
            "All metrics should have a 'job' label, but found metrics without it"
        )


class TestPrometheusTargetDetails:
    """Test detailed target information."""

    def test_get_all_targets_details(self, prometheus_url: str):
        """Get detailed information about all scrape targets."""
        targets = get_targets(prometheus_url)
        assert len(targets) > 0, "Should have at least one active target"

        optional_services = ["dora-api"]
        down_core_targets = [
            f"{t.get('labels', {}).get('job', 'unknown')}/{t.get('labels', {}).get('instance', 'unknown')}"
            for t in targets
            if t.get("health") != "up"
            and t.get("labels", {}).get("job") not in optional_services
        ]

        assert len(down_core_targets) == 0, (
            f"Core targets should be healthy, but these are down: {', '.join(down_core_targets)}"
        )

    def test_otel_collector_target_labels(self, prometheus_url: str):
        """Test that OTel Collector target has correct labels."""
        targets = get_targets(prometheus_url)

        otel_targets = [
            t for t in targets if t.get("labels", {}).get("job") == "otel-collector"
        ]
        assert len(otel_targets) > 0, "Should have OTel Collector target"

        labels = otel_targets[0].get("labels", {})
        assert labels.get("component") == "otel-collector", (
            "Should have component=otel-collector label"
        )
        assert labels.get("service") == "telemetry", (
            "Should have service=telemetry label"
        )


class TestPrometheusMetricCardinality:
    """Test that metric cardinality is reasonable."""

    def test_metric_cardinality_is_reasonable(self, prometheus_url: str):
        """Test that we don't have excessive metric cardinality."""
        data = query_prometheus(prometheus_url, 'count({__name__=~".+"})')

        results = data.get("result", [])
        if len(results) > 0:
            total_series = int(float(results[0].get("value", [0, "0"])[1]))
            max_expected_series = int(os.getenv("MAX_SERIES_CARDINALITY", "10000"))

            assert total_series < max_expected_series, (
                f"Metric cardinality is too high: {total_series} series "
                f"(max: {max_expected_series})"
            )

    def test_no_excessive_label_combinations(self, prometheus_url: str):
        """Test that no single metric has excessive label combinations."""
        metrics_to_check = ["up", "scrape_duration_seconds", "otelcol_process_uptime"]

        for metric in metrics_to_check:
            data = query_prometheus(prometheus_url, f"count({metric}) by (__name__)")
            results = data.get("result", [])

            if len(results) > 0:
                count = int(float(results[0].get("value", [0, "0"])[1]))
                max_expected = 100  # Reasonable limit per metric

                assert count < max_expected, (
                    f"Metric '{metric}' has too many series: {count} (max: {max_expected})"
                )
