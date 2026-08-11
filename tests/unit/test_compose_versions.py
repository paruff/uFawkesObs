"""
Unit tests that assert Docker Compose image versions match expected targets.

These tests catch accidental drift — e.g. someone changing a version string
during an unrelated PR. Must pass before any version upgrade PR is merged.

Run:  pytest tests/unit/test_compose_versions.py -v
      (no running stack required — reads compose.yaml statically)
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path to compose.yaml relative to this file's directory
# ---------------------------------------------------------------------------
COMPOSE_PATH = pathlib.Path(__file__).resolve().parents[2] / "compose.yaml"

# ---------------------------------------------------------------------------
# Expected image strings — update these ONLY when upgrading a service.
# The key is the Docker Compose service name; the value is the full
# registry/repo:tag string that must appear in compose.yaml.
# ---------------------------------------------------------------------------
EXPECTED_VERSIONS: dict[str, str] = {
    "otel-collector": "otel/opentelemetry-collector-contrib:0.120.0",
    "prometheus": "prom/prometheus:v3.5.4",
    "alertmanager": "prom/alertmanager:v0.28.0",
    "tempo": "grafana/tempo:2.10.5",
    "loki": "grafana/loki:3.3.2",
    "alloy": "grafana/alloy:v1.12.2",
    "grafana": "grafana/grafana:12.3.7",
    "alertmanager-discord": "rogerrum/alertmanager-discord:1.0.7",
}

EXPECTED_LOCALHOST_BINDINGS: dict[str, str] = {
    "tempo": "127.0.0.1:3200:3200",
    "loki": "127.0.0.1:3100:3100",
    "prometheus": "127.0.0.1:9090:9090",
    "alertmanager": "127.0.0.1:9093:9093",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def compose_data() -> dict:
    """Load and return the parsed compose.yaml as a dict."""
    if not COMPOSE_PATH.exists():
        pytest.fail(f"compose.yaml not found at {COMPOSE_PATH}")
    with open(COMPOSE_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "compose.yaml must parse to a mapping"
    return data


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestComposeImageVersions:
    """Verify every tracked service has the exact expected image tag."""

    @pytest.mark.parametrize(
        "service,expected_image",
        list(EXPECTED_VERSIONS.items()),
        ids=list(EXPECTED_VERSIONS.keys()),
    )
    def test_image_version_matches(
        self, compose_data: dict, service: str, expected_image: str
    ) -> None:
        """Assert the service exists and its image string matches exactly."""
        services = compose_data.get("services")
        assert services is not None, "compose.yaml has no 'services' key"
        assert service in services, (
            f"Service '{service}' is missing from compose.yaml — "
            f"cannot verify image version"
        )

        actual_image = services[service].get("image")
        assert actual_image is not None, (
            f"Service '{service}' has no 'image' field in compose.yaml"
        )
        assert actual_image == expected_image, (
            f"Service '{service}' image mismatch:\n"
            f"  expected: {expected_image}\n"
            f"  actual:   {actual_image}"
        )

    @pytest.mark.parametrize(
        "service,expected_image",
        list(EXPECTED_VERSIONS.items()),
        ids=list(EXPECTED_VERSIONS.keys()),
    )
    def test_image_not_latest(
        self, compose_data: dict, service: str, expected_image: str
    ) -> None:
        """Guard against accidental use of the 'latest' tag."""
        services = compose_data.get("services", {})
        if service not in services:
            pytest.skip(f"Service '{service}' not present — covered by other test")
        actual_image = services[service].get("image", "")
        tag = actual_image.split(":")[-1] if ":" in actual_image else ""
        assert tag != "latest", (
            f"Service '{service}' uses ':latest' tag — pin to a specific version"
        )

    @pytest.mark.parametrize(
        "service,expected_image",
        list(EXPECTED_VERSIONS.items()),
        ids=list(EXPECTED_VERSIONS.keys()),
    )
    def test_image_tag_not_empty(
        self, compose_data: dict, service: str, expected_image: str
    ) -> None:
        """Guard against an empty or missing tag."""
        services = compose_data.get("services", {})
        if service not in services:
            pytest.skip(f"Service '{service}' not present — covered by other test")
        actual_image = services[service].get("image", "")
        assert ":" in actual_image, (
            f"Service '{service}' image '{actual_image}' has no tag — "
            f"expected '{expected_image}'"
        )
        tag = actual_image.split(":")[-1]
        assert tag != "", (
            f"Service '{service}' image has an empty tag — expected '{expected_image}'"
        )


class TestComposeLocalhostBindings:
    """Verify sensitive backend HTTP ports are localhost-only by default."""

    @pytest.mark.parametrize(
        "service,expected_port_binding",
        list(EXPECTED_LOCALHOST_BINDINGS.items()),
        ids=list(EXPECTED_LOCALHOST_BINDINGS.keys()),
    )
    def test_backend_http_port_is_localhost_only(
        self, compose_data: dict, service: str, expected_port_binding: str
    ) -> None:
        """Assert the expected localhost-only host binding is present."""
        services = compose_data.get("services", {})
        assert service in services, (
            f"Service '{service}' is missing from compose.yaml — "
            "cannot verify localhost-only binding"
        )

        ports = services[service].get("ports")
        assert isinstance(ports, list), (
            f"Service '{service}' has no valid 'ports' list in compose.yaml"
        )
        assert expected_port_binding in ports, (
            f"Service '{service}' must include localhost-only binding "
            f"'{expected_port_binding}', found: {ports}"
        )
