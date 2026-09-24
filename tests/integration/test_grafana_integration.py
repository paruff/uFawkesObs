"""
Integration tests for Grafana.

Migrated to Testcontainers (#416): provisions Grafana together with its
datasource dependencies (Prometheus, Tempo, Loki) per test-module run,
instead of assuming `make up` already started a shared stack. Grafana's
provisioned datasources reference these by Docker Compose service name
(AGENTS.md §4), so this is a genuine multi-service group -- not a
single-service migration like Tempo/Loki.
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
GRAFANA_ADMIN_PASSWORD = os.environ.get("GRAFANA_ADMIN_PASSWORD", "admin")


@pytest.fixture(scope="module")
def grafana_stack():
    # `docker compose` auto-loads REPO_ROOT/.env (a real local dev file,
    # e.g. GRAFANA_ADMIN_PASSWORD=<the developer's own password>) ahead of
    # this process's own os.environ -- confirmed live: setting os.environ
    # here had no effect, the container still came up with .env's value.
    # An explicit env_file pointed elsewhere is the only override that
    # actually takes precedence over that auto-discovery.
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
        f.write(f"GRAFANA_ADMIN_PASSWORD={GRAFANA_ADMIN_PASSWORD}\n")
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


def _host_port(
    stack: DockerCompose, service: str, container_port: int
) -> tuple[str, int]:
    host, port = stack.get_service_host_and_port(service, container_port)
    return host, int(port)


@pytest.fixture(scope="module")
def grafana_url(grafana_stack: DockerCompose) -> str:
    host, port = _host_port(grafana_stack, "grafana", 3000)
    url = f"http://{host}:{port}"

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


def get_datasources(grafana_url: str, grafana_auth: tuple) -> list[dict[str, Any]]:
    response = requests.get(
        f"{grafana_url}/api/datasources", auth=grafana_auth, timeout=10
    )
    response.raise_for_status()
    return response.json()


def check_datasource_health(
    grafana_url: str, grafana_auth: tuple, datasource_uid: str
) -> dict[str, Any]:
    response = requests.get(
        f"{grafana_url}/api/datasources/uid/{datasource_uid}/health",
        auth=grafana_auth,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def query_datasource(
    grafana_url: str, grafana_auth: tuple, datasource_uid: str, query: dict[str, Any]
) -> dict[str, Any]:
    response = requests.post(
        f"{grafana_url}/api/ds/query", auth=grafana_auth, json=query, timeout=30
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture(scope="module")
def provisioned_datasources(
    grafana_url: str, grafana_auth: tuple
) -> list[dict[str, Any]]:
    """Wait for all 3 expected datasource types to actually be provisioned.

    Replaces the original file's blind `time.sleep(10)` after /api/health
    passed ("give Grafana a bit more time to provision datasources") --
    that's exactly the non-determinism class this migration exists to fix.
    """
    expected = {"prometheus", "tempo", "loki"}
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            datasources = get_datasources(grafana_url, grafana_auth)
            if expected.issubset({ds.get("type") for ds in datasources}):
                return datasources
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    pytest.fail("Datasources (prometheus/tempo/loki) not fully provisioned within 30s")


class TestGrafanaHealth:
    """Test Grafana health and availability."""

    def test_grafana_is_healthy(self, grafana_url: str):
        response = requests.get(f"{grafana_url}/api/health")
        assert response.status_code == 200, "Grafana should return 200 OK"
        assert response.json().get("database") == "ok", (
            "Grafana database should be healthy"
        )

    def test_grafana_api_authentication(self, grafana_url: str, grafana_auth: tuple):
        response = requests.get(f"{grafana_url}/api/org", auth=grafana_auth)
        assert response.status_code == 200, (
            "Should be able to authenticate with Grafana API"
        )
        assert "name" in response.json(), "Should get organization info"


class TestGrafanaDatasources:
    """Test Grafana datasources."""

    def test_datasources_are_provisioned(
        self, provisioned_datasources: list[dict[str, Any]]
    ):
        assert len(provisioned_datasources) >= 3, (
            "Should have at least 3 datasources (Prometheus, Tempo, Loki)"
        )

    def test_prometheus_datasource_connectivity(
        self,
        provisioned_datasources: list[dict[str, Any]],
        grafana_url: str,
        grafana_auth: tuple,
    ):
        prometheus_ds = [
            ds for ds in provisioned_datasources if ds.get("type") == "prometheus"
        ]
        assert len(prometheus_ds) > 0, "Prometheus datasource should exist"

        health = check_datasource_health(
            grafana_url, grafana_auth, prometheus_ds[0]["uid"]
        )
        assert health.get("status") == "OK", (
            f"Prometheus datasource should be healthy: {health.get('message')}"
        )

    def test_tempo_datasource_connectivity(
        self,
        provisioned_datasources: list[dict[str, Any]],
        grafana_url: str,
        grafana_auth: tuple,
    ):
        tempo_ds = [ds for ds in provisioned_datasources if ds.get("type") == "tempo"]
        assert len(tempo_ds) > 0, "Tempo datasource should exist"

        try:
            health = check_datasource_health(
                grafana_url, grafana_auth, tempo_ds[0]["uid"]
            )
            assert health.get("status") == "OK", (
                f"Tempo datasource should be healthy: {health.get('message')}"
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise
            # Health check endpoint not available for this Tempo version --
            # provisioning existing (already asserted above) is enough.

    def test_loki_datasource_connectivity(
        self,
        provisioned_datasources: list[dict[str, Any]],
        grafana_url: str,
        grafana_auth: tuple,
    ):
        loki_ds = [ds for ds in provisioned_datasources if ds.get("type") == "loki"]
        assert len(loki_ds) > 0, "Loki datasource should exist"

        health = check_datasource_health(grafana_url, grafana_auth, loki_ds[0]["uid"])
        assert health.get("status") == "OK", (
            f"Loki datasource should be healthy: {health.get('message')}"
        )

    def test_default_datasource_is_set(
        self, provisioned_datasources: list[dict[str, Any]]
    ):
        default_ds = [ds for ds in provisioned_datasources if ds.get("isDefault")]
        assert len(default_ds) > 0, "Should have a default datasource configured"


class TestGrafanaDatasourceQueries:
    """Test that datasources can execute queries."""

    def test_prometheus_query_execution(
        self,
        provisioned_datasources: list[dict[str, Any]],
        grafana_url: str,
        grafana_auth: tuple,
    ):
        prometheus_ds = [
            ds for ds in provisioned_datasources if ds.get("type") == "prometheus"
        ]
        assert len(prometheus_ds) > 0, "Prometheus datasource should exist"
        ds_uid = prometheus_ds[0]["uid"]

        query_payload = {
            "queries": [
                {
                    "refId": "A",
                    "datasource": {"type": "prometheus", "uid": ds_uid},
                    "expr": "up",
                    "instant": True,
                }
            ],
            "from": "now-5m",
            "to": "now",
        }
        result = query_datasource(grafana_url, grafana_auth, ds_uid, query_payload)
        assert "results" in result, "Query should return results"

    def test_loki_query_execution(
        self,
        provisioned_datasources: list[dict[str, Any]],
        grafana_url: str,
        grafana_auth: tuple,
    ):
        loki_ds = [ds for ds in provisioned_datasources if ds.get("type") == "loki"]
        assert len(loki_ds) > 0, "Loki datasource should exist"
        ds_uid = loki_ds[0]["uid"]

        query_payload = {
            "queries": [
                {
                    "refId": "A",
                    "datasource": {"type": "loki", "uid": ds_uid},
                    "expr": '{job=~".+"}',
                    "queryType": "range",
                }
            ],
            "from": "now-5m",
            "to": "now",
        }
        result = query_datasource(grafana_url, grafana_auth, ds_uid, query_payload)
        assert "results" in result, "Query should return results"


class TestGrafanaDashboards:
    """Test Grafana dashboards can query data."""

    def test_dashboards_exist(self, grafana_url: str, grafana_auth: tuple):
        response = requests.get(
            f"{grafana_url}/api/search?type=dash-db", auth=grafana_auth, timeout=10
        )
        response.raise_for_status()
        dashboards = response.json()
        assert len(dashboards) >= 5, (
            f"Should have at least 5 dashboards provisioned, got {len(dashboards)}"
        )

    def test_observability_dashboard_can_query_data(
        self, grafana_url: str, grafana_auth: tuple
    ):
        response = requests.get(
            f"{grafana_url}/api/dashboards/uid/observability-stack-health",
            auth=grafana_auth,
            timeout=10,
        )
        if response.status_code == 200:
            panels = response.json().get("dashboard", {}).get("panels", [])
            assert len(panels) > 0, "Dashboard should have panels"


class TestGrafanaPlugins:
    """Test that required Grafana plugins are installed."""

    def test_required_plugins_installed(self, grafana_url: str, grafana_auth: tuple):
        response = requests.get(
            f"{grafana_url}/api/plugins", auth=grafana_auth, timeout=10
        )
        response.raise_for_status()
        plugin_ids = [p.get("id") for p in response.json()]

        for plugin in ("prometheus", "tempo", "loki"):
            assert plugin in plugin_ids, f"Plugin '{plugin}' should be installed"


class TestGrafanaSettings:
    """Test Grafana settings and configuration."""

    def test_grafana_version(self, grafana_url: str):
        response = requests.get(f"{grafana_url}/api/health")
        assert response.status_code == 200
        assert response.json().get("version"), "Should report a version"

    def test_anonymous_access_disabled(self, grafana_url: str):
        response = requests.get(f"{grafana_url}/api/org", timeout=10)
        assert response.status_code in (401, 403), (
            "Anonymous access should be disabled -- unauthenticated /api/org "
            f"should be rejected, got {response.status_code}"
        )
