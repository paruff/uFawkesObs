"""
Integration tests for Grafana dashboard provisioning and validation.
Tests that all pre-built dashboards are correctly provisioned and accessible.

Migrated to Testcontainers (#416): TestDashboardProvisioning and
TestDashboardDataSources need the full `core` profile (Grafana +
Prometheus + Tempo + Loki datasources provisioned), provisioned per
test-module run instead of assuming `make up` already started a shared
stack. TestDashboardFiles / TestNewPlatformDashboards /
TestNewServiceDashboards read local JSON files directly and need no
running stack at all -- left untouched.
"""

from __future__ import annotations

import json
import os
import pathlib
import tempfile
import time
from typing import Any

import pytest
import requests
from testcontainers.compose import DockerCompose

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GRAFANA_ADMIN_PASSWORD = os.environ.get("GRAFANA_ADMIN_PASSWORD", "admin")

DASHBOARD_DIR = REPO_ROOT / "config" / "grafana" / "dashboards"
PLATFORM_DASHBOARD_DIR = REPO_ROOT / "dashboards" / "platform"
SERVICE_DASHBOARD_DIR = REPO_ROOT / "dashboards" / "services"

DASHBOARD_FILES = [
    "observability-stack-health.json",
    "iot-devices-mqtt.json",
    "application-performance.json",
    "infrastructure-overview.json",
]

PLATFORM_DASHBOARD_FILES = [
    "global-health.json",
    "prometheus-overview.json",
    "loki-overview.json",
    "tempo-overview.json",
    "alloy-overview.json",
    "alertmanager-overview.json",
    "storage-capacity.json",
    "ingestion-health.json",
]

SERVICE_DASHBOARD_FILES = [
    "service-overview.json",
    "service-latency.json",
    "service-errors.json",
    "service-saturation.json",
    "service-debug.json",
    "service-slo.json",
    "service-capacity.json",
]


@pytest.fixture(scope="module")
def dashboards_stack():
    # Same GRAFANA_ADMIN_PASSWORD/.env-precedence fix as #416's Grafana and
    # Prometheus migrations, plus SLACK_WEBHOOK_URL for the whole-profile
    # secrets requirement -- see those PRs for why both are needed.
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
        f.write(f"GRAFANA_ADMIN_PASSWORD={GRAFANA_ADMIN_PASSWORD}\n")
        f.write(f"SLACK_WEBHOOK_URL={os.environ.get('SLACK_WEBHOOK_URL', '')}\n")
        env_file_path = f.name

    try:
        with DockerCompose(
            context=str(REPO_ROOT),
            compose_file_name="compose.yaml",
            env_file=env_file_path,
            services=["grafana", "prometheus", "tempo", "loki"],
            profiles=["core"],
            wait=True,
        ) as compose:
            yield compose
    finally:
        os.unlink(env_file_path)


@pytest.fixture(scope="module")
def grafana_base_url(dashboards_stack: DockerCompose) -> str:
    host, port = dashboards_stack.get_service_host_and_port("grafana", 3000)
    url = f"http://{host}:{int(port)}"

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{url}/api/health", timeout=5).status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        pytest.fail("Grafana did not report /api/health within 60s")
    return url


@pytest.fixture(scope="module")
def grafana_auth() -> tuple[str, str]:
    return ("admin", GRAFANA_ADMIN_PASSWORD)


@pytest.fixture(scope="module")
def provisioned_dashboards(
    grafana_base_url: str, grafana_auth: tuple
) -> list[dict[str, Any]]:
    """Wait for all 4 legacy dashboards to actually be provisioned --
    replaces relying on wait_for_grafana's readiness alone."""
    expected_uids = {
        "observability-stack-health",
        "iot-devices-mqtt",
        "application-performance",
        "infrastructure-overview",
    }
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            dashboards = get_dashboards(grafana_base_url, grafana_auth)
            if expected_uids.issubset({d["uid"] for d in dashboards}):
                return dashboards
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    pytest.fail("Not all expected dashboards were provisioned within 30s")


def get_dashboards(grafana_base_url: str, grafana_auth: tuple) -> list[dict[str, Any]]:
    response = requests.get(
        f"{grafana_base_url}/api/search?type=dash-db", auth=grafana_auth, timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_dashboard_by_uid(
    grafana_base_url: str, grafana_auth: tuple, uid: str
) -> dict[str, Any]:
    response = requests.get(
        f"{grafana_base_url}/api/dashboards/uid/{uid}", auth=grafana_auth, timeout=10
    )
    response.raise_for_status()
    return response.json()


class TestDashboardProvisioning:
    """Test dashboard provisioning and structure."""

    def test_grafana_is_accessible(self, grafana_base_url: str):
        response = requests.get(f"{grafana_base_url}/api/health")
        assert response.status_code == 200
        assert response.json().get("database") == "ok", (
            "Grafana database should be healthy"
        )

    def test_all_dashboards_provisioned(
        self, provisioned_dashboards: list[dict[str, Any]]
    ):
        expected_uids = [
            "observability-stack-health",
            "iot-devices-mqtt",
            "application-performance",
            "infrastructure-overview",
        ]
        provisioned_uids = [d["uid"] for d in provisioned_dashboards]
        for uid in expected_uids:
            assert uid in provisioned_uids, f"Dashboard '{uid}' should be provisioned"

    def test_observability_stack_health_dashboard(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        dashboard = get_dashboard_by_uid(
            grafana_base_url, grafana_auth, "observability-stack-health"
        )
        assert dashboard is not None
        assert "dashboard" in dashboard

        dash = dashboard["dashboard"]
        assert dash["title"] == "Observability Stack Health"
        assert "observability" in dash["tags"]

        panels = dash.get("panels", [])
        assert len(panels) > 0, "Dashboard should have panels"

        panel_titles = [p.get("title", "") for p in panels]
        assert "Prometheus Status" in panel_titles, (
            "Should have Prometheus status panel"
        )
        assert "OTel Collector Status" in panel_titles, (
            "Should have OTel Collector status panel"
        )

    def test_iot_devices_mqtt_dashboard(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        dashboard = get_dashboard_by_uid(
            grafana_base_url, grafana_auth, "iot-devices-mqtt"
        )
        dash = dashboard["dashboard"]
        assert dash["title"] == "IoT Devices & MQTT"
        assert "iot" in dash["tags"] or "mqtt" in dash["tags"]

        panels = dash.get("panels", [])
        assert len(panels) > 0, "Dashboard should have panels"
        panel_titles = [p.get("title", "") for p in panels]
        assert "Active Connections" in panel_titles
        assert "Message Rate by Topic" in panel_titles

        var_names = [
            v.get("name", "") for v in dash.get("templating", {}).get("list", [])
        ]
        assert "topic" in var_names, "Should have topic variable for filtering"

    def test_application_performance_dashboard(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        dashboard = get_dashboard_by_uid(
            grafana_base_url, grafana_auth, "application-performance"
        )
        dash = dashboard["dashboard"]
        assert dash["title"] == "Application Performance"
        assert "application" in dash["tags"] or "performance" in dash["tags"]

        panel_titles = [p.get("title", "") for p in dash.get("panels", [])]
        assert "Total Request Rate" in panel_titles
        assert "Error Rate" in panel_titles
        assert "p95 Latency" in panel_titles

        var_names = [
            v.get("name", "") for v in dash.get("templating", {}).get("list", [])
        ]
        assert "service" in var_names, "Should have service variable for filtering"

    def test_infrastructure_overview_dashboard(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        dashboard = get_dashboard_by_uid(
            grafana_base_url, grafana_auth, "infrastructure-overview"
        )
        dash = dashboard["dashboard"]
        assert dash["title"] == "Infrastructure Overview"
        assert "infrastructure" in dash["tags"] or "containers" in dash["tags"]

        panel_titles = [p.get("title", "") for p in dash.get("panels", [])]
        assert "Running Containers" in panel_titles
        assert "Container CPU Usage" in panel_titles
        assert "Container Memory Usage" in panel_titles

        var_names = [
            v.get("name", "") for v in dash.get("templating", {}).get("list", [])
        ]
        assert "container" in var_names, "Should have container variable for filtering"

    def test_dashboard_auto_refresh(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        for uid in (
            "observability-stack-health",
            "iot-devices-mqtt",
            "application-performance",
            "infrastructure-overview",
        ):
            dash = get_dashboard_by_uid(grafana_base_url, grafana_auth, uid)[
                "dashboard"
            ]
            refresh = dash.get("refresh", "")
            assert refresh == "30s", (
                f"Dashboard '{uid}' should have 30s refresh interval"
            )

    def test_dashboard_time_range(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        for uid in (
            "observability-stack-health",
            "iot-devices-mqtt",
            "application-performance",
            "infrastructure-overview",
        ):
            dash = get_dashboard_by_uid(grafana_base_url, grafana_auth, uid)[
                "dashboard"
            ]
            time_config = dash.get("time", {})
            assert time_config, f"Dashboard '{uid}' should have time range configured"
            assert "from" in time_config
            assert "to" in time_config


class TestDashboardDataSources:
    """Test that dashboards use correct datasources."""

    def test_prometheus_datasource_configured(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        response = requests.get(
            f"{grafana_base_url}/api/datasources", auth=grafana_auth, timeout=10
        )
        response.raise_for_status()
        datasources = response.json()

        prometheus_ds = [ds for ds in datasources if ds.get("type") == "prometheus"]
        assert len(prometheus_ds) > 0, "Prometheus datasource should be configured"
        assert any(ds.get("isDefault") for ds in prometheus_ds), (
            "Prometheus should be set as default datasource"
        )

    def test_tempo_datasource_configured(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        response = requests.get(
            f"{grafana_base_url}/api/datasources", auth=grafana_auth, timeout=10
        )
        response.raise_for_status()
        tempo_ds = [ds for ds in response.json() if ds.get("type") == "tempo"]
        assert len(tempo_ds) > 0, "Tempo datasource should be configured"

    def test_loki_datasource_configured(
        self,
        provisioned_dashboards: list[dict[str, Any]],
        grafana_base_url: str,
        grafana_auth: tuple,
    ):
        response = requests.get(
            f"{grafana_base_url}/api/datasources", auth=grafana_auth, timeout=10
        )
        response.raise_for_status()
        loki_ds = [ds for ds in response.json() if ds.get("type") == "loki"]
        assert len(loki_ds) > 0, "Loki datasource should be configured"


class TestDashboardFiles:
    """Test dashboard JSON files in the repository. No running stack needed."""

    def test_dashboard_files_exist(self):
        for filename in DASHBOARD_FILES:
            assert (DASHBOARD_DIR / filename).exists(), (
                f"Dashboard file '{filename}' should exist"
            )

    def test_dashboard_json_valid(self):
        for filename in DASHBOARD_FILES:
            with open(DASHBOARD_DIR / filename) as f:
                try:
                    dashboard = json.load(f)
                    assert "title" in dashboard
                    assert "panels" in dashboard
                except json.JSONDecodeError as e:
                    pytest.fail(f"Dashboard '{filename}' has invalid JSON: {e}")

    def test_dashboard_uids_unique(self):
        uids = []
        for filename in DASHBOARD_FILES:
            with open(DASHBOARD_DIR / filename) as f:
                uid = json.load(f).get("uid")
                assert uid, f"Dashboard '{filename}' should have a UID"
                assert uid not in uids, f"Dashboard UID '{uid}' is not unique"
                uids.append(uid)


class TestNewPlatformDashboards:
    """Test new platform dashboard JSON files in the repository."""

    def test_platform_dashboard_files_exist(self):
        for filename in PLATFORM_DASHBOARD_FILES:
            assert (PLATFORM_DASHBOARD_DIR / filename).exists(), (
                f"Platform dashboard file '{filename}' should exist"
            )

    def test_platform_dashboard_json_valid(self):
        for filename in PLATFORM_DASHBOARD_FILES:
            with open(PLATFORM_DASHBOARD_DIR / filename) as f:
                try:
                    dashboard = json.load(f)
                    assert "title" in dashboard
                    assert "panels" in dashboard
                    assert "uid" in dashboard
                    assert dashboard["uid"].startswith("platform-")

                    var_names = [
                        v.get("name", "")
                        for v in dashboard.get("templating", {}).get("list", [])
                    ]
                    assert "datasource" in var_names, (
                        f"Dashboard '{filename}' should have datasource variable"
                    )
                except json.JSONDecodeError as e:
                    pytest.fail(
                        f"Platform dashboard '{filename}' has invalid JSON: {e}"
                    )

    def test_platform_dashboard_uids_unique(self):
        uids = []
        for filename in PLATFORM_DASHBOARD_FILES:
            with open(PLATFORM_DASHBOARD_DIR / filename) as f:
                uid = json.load(f).get("uid")
                assert uid, f"Dashboard '{filename}' should have a UID"
                assert uid not in uids, f"Dashboard UID '{uid}' is not unique"
                uids.append(uid)


class TestNewServiceDashboards:
    """Test new service dashboard JSON files in the repository."""

    def test_service_dashboard_files_exist(self):
        for filename in SERVICE_DASHBOARD_FILES:
            assert (SERVICE_DASHBOARD_DIR / filename).exists(), (
                f"Service dashboard file '{filename}' should exist"
            )

    def test_service_dashboard_json_valid(self):
        for filename in SERVICE_DASHBOARD_FILES:
            with open(SERVICE_DASHBOARD_DIR / filename) as f:
                try:
                    dashboard = json.load(f)
                    assert "title" in dashboard
                    assert "panels" in dashboard
                    assert "uid" in dashboard
                    assert dashboard["uid"].startswith("ufawkesobs-service-")

                    var_names = [
                        v.get("name", "")
                        for v in dashboard.get("templating", {}).get("list", [])
                    ]
                    assert "datasource" in var_names
                    assert "service" in var_names
                except json.JSONDecodeError as e:
                    pytest.fail(f"Service dashboard '{filename}' has invalid JSON: {e}")

    def test_service_dashboard_uids_unique(self):
        uids = []
        for filename in SERVICE_DASHBOARD_FILES:
            with open(SERVICE_DASHBOARD_DIR / filename) as f:
                uid = json.load(f).get("uid")
                assert uid, f"Dashboard '{filename}' should have a UID"
                assert uid not in uids, f"Dashboard UID '{uid}' is not unique"
                uids.append(uid)

    def test_service_overview_has_golden_signals(self):
        with open(SERVICE_DASHBOARD_DIR / "service-overview.json") as f:
            panels = json.load(f).get("panels", [])
            panel_titles = [p.get("title", "").lower() for p in panels]

            assert any(
                "traffic" in t or "request" in t or "rps" in t for t in panel_titles
            ), "Service overview should have Traffic metric panel"
            assert any(
                "latency" in t or "duration" in t or "p99" in t or "p95" in t
                for t in panel_titles
            ), "Service overview should have Latency metric panel"
            assert any("error" in t for t in panel_titles), (
                "Service overview should have Errors metric panel"
            )
            assert any(
                "saturation" in t or "cpu" in t or "memory" in t for t in panel_titles
            ), "Service overview should have Saturation metric panel"
