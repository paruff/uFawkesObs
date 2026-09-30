"""
Pytest configuration and shared fixtures for integration tests.
"""

import os
import subprocess
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
import requests
from testcontainers.compose import DockerCompose

# Configuration
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
OTEL_COLLECTOR_URL = os.getenv("OTEL_COLLECTOR_URL", "http://localhost:8888")
REPO_ROOT = Path(__file__).resolve().parents[2]


def _reset_stale_compose_stack() -> None:
    """Remove any leftover repo stack so each module starts with a clean Docker state."""
    env = {**os.environ, "COMPOSE_PROJECT_NAME": "ufawkesobs"}
    subprocess.run(
        ["docker", "compose", "--profile", "core", "down", "-v", "--remove-orphans"],
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for name in [
        "alertmanager",
        "prometheus",
        "tempo",
        "loki",
        "grafana",
        "alloy",
        "otel-collector",
    ]:
        subprocess.run(
            ["docker", "rm", "-f", name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


@contextmanager
def compose_stack(
    prefix: str,
    *,
    env_file: str | list[str] | None = None,
    services: list[str] | None = None,
    profiles: list[str] | None = None,
):
    """Start a module-local stack while keeping the Compose project namespace isolated from the shared repo stack."""
    _reset_stale_compose_stack()
    previous_project = os.environ.get("COMPOSE_PROJECT_NAME")
    os.environ["COMPOSE_PROJECT_NAME"] = f"ufawkesobs-{prefix}-{uuid.uuid4().hex[:8]}"
    try:
        with DockerCompose(
            context=str(REPO_ROOT),
            compose_file_name="compose.yaml",
            env_file=env_file,
            services=services,
            profiles=profiles,
            wait=True,
        ) as compose:
            yield compose
    finally:
        if previous_project is None:
            os.environ.pop("COMPOSE_PROJECT_NAME", None)
        else:
            os.environ["COMPOSE_PROJECT_NAME"] = previous_project


@pytest.fixture(scope="session")
def prometheus_base_url() -> str:
    """Provide Prometheus base URL."""
    return PROMETHEUS_URL


@pytest.fixture(scope="session")
def otel_collector_base_url() -> str:
    """Provide OpenTelemetry Collector base URL."""
    return OTEL_COLLECTOR_URL


@pytest.fixture(scope="session")
def wait_for_prometheus(prometheus_base_url: str) -> None:
    """Wait for Prometheus to be ready."""
    max_retries = 30
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{prometheus_base_url}/-/healthy", timeout=5)
            if response.status_code == 200:
                print(f"✅ Prometheus is ready after {attempt + 1} attempts")
                return
        except requests.exceptions.RequestException:
            pass

        time.sleep(retry_interval)

    pytest.fail("Prometheus did not become ready in time")


@pytest.fixture(scope="session")
def wait_for_otel_collector(otel_collector_base_url: str) -> None:
    """Wait for OpenTelemetry Collector to be ready."""
    max_retries = 30
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{otel_collector_base_url}/metrics", timeout=5)
            # Check for any valid metrics response (should contain metric names)
            if response.status_code == 200 and len(response.text) > 100:
                print(f"✅ OTel Collector is ready after {attempt + 1} attempts")
                return
        except requests.exceptions.RequestException:
            pass

        time.sleep(retry_interval)

    pytest.fail("OTel Collector did not become ready in time")


@pytest.fixture(scope="function")
def wait_for_scrape_cycle() -> None:
    """
    Wait for at least one Prometheus scrape cycle to complete.
    Default scrape interval is 30s, so we wait 35s to be safe.
    """
    print("⏳ Waiting for Prometheus scrape cycle (35 seconds)...")
    time.sleep(35)
    print("✅ Scrape cycle wait completed")


def query_prometheus(prometheus_base_url: str, query: str) -> dict[str, Any]:
    """
    Helper function to query Prometheus.

    Args:
        prometheus_base_url: Base URL for Prometheus
        query: PromQL query string

    Returns:
        JSON response from Prometheus
    """
    response = requests.get(
        f"{prometheus_base_url}/api/v1/query", params={"query": query}, timeout=10
    )
    response.raise_for_status()
    return response.json()


def parse_prometheus_metrics(text: str) -> dict[str, list]:
    """
    Parse Prometheus text format metrics into a dictionary.

    Args:
        text: Prometheus text format metrics

    Returns:
        Dictionary mapping metric names to lists of metric lines
    """
    metrics = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Extract metric name (before '{' or ' ')
        if "{" in line:
            metric_name = line.split("{")[0]
        elif " " in line:
            metric_name = line.split(" ")[0]
        else:
            continue

        if metric_name not in metrics:
            metrics[metric_name] = []
        metrics[metric_name].append(line)

    return metrics


@pytest.fixture(scope="function")
def prometheus_query(prometheus_base_url: str):
    """Fixture that provides a Prometheus query function."""

    def _query(query: str) -> dict[str, Any]:
        return query_prometheus(prometheus_base_url, query)

    return _query


@pytest.fixture(scope="function")
def parse_metrics():
    """Fixture that provides a metric parsing function."""
    return parse_prometheus_metrics
