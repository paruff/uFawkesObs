"""
Step definitions for Core Observability Substrate (M1) feature.
"""

from __future__ import annotations

import subprocess
import yaml
from pathlib import Path
from pytest_bdd import given, then, parsers

from tests.acceptance.runtime import ObservabilityStack


@given("the compose.yaml is loaded")
def compose_loaded(stack: ObservabilityStack) -> None:
    """Compose.yaml is loaded via the stack fixture."""
    pass  # Stack fixture handles this


@then(parsers.parse('no service should use the "{tag}" image tag'))
def no_service_uses_latest(tag: str, stack: ObservabilityStack) -> None:
    """Assert no service uses the 'latest' image tag (or any specified tag)."""
    compose_path = Path(stack.compose_dir) / "compose.yaml"
    content = yaml.safe_load(compose_path.read_text())

    services = content.get("services", {})
    for service_name, service_def in services.items():
        image = service_def.get("image", "")
        if tag in image and ":latest" in image:
            raise AssertionError(f"Service '{service_name}' uses 'latest' tag: {image}")

    print(f"✅ No service uses '{tag}' image tag")


@then("all services should have a healthcheck")
def all_services_have_healthcheck(stack: ObservabilityStack) -> None:
    """Assert all services have healthcheck definitions."""
    compose_path = Path(stack.compose_dir) / "compose.yaml"
    content = yaml.safe_load(compose_path.read_text())

    services = content.get("services", {})
    for service_name, service_def in services.items():
        healthcheck = service_def.get("healthcheck")
        assert healthcheck is not None, f"Service '{service_name}' missing healthcheck"

    print(f"✅ All {len(services)} services have healthcheck definitions")


@then(parsers.parse('service "{service}" should have image "{image}"'))
def service_has_image(service: str, image: str, stack: ObservabilityStack) -> None:
    """Assert a specific service has the expected image."""
    compose_path = Path(stack.compose_dir) / "compose.yaml"
    content = yaml.safe_load(compose_path.read_text())

    services = content.get("services", {})
    service_def = services.get(service)
    assert service_def is not None, f"Service '{service}' not found in compose.yaml"

    actual_image = service_def.get("image", "")
    assert actual_image == image, (
        f"Service '{service}' has image '{actual_image}', expected '{image}'"
    )
    print(f"✅ Service '{service}' has correct image: {image}")


@then(parsers.parse('service "{service}" should be in network "{network}"'))
def service_in_network(service: str, network: str, stack: ObservabilityStack) -> None:
    """Assert a service is connected to a specific network."""
    compose_path = Path(stack.compose_dir) / "compose.yaml"
    content = yaml.safe_load(compose_path.read_text())

    services = content.get("services", {})
    service_def = services.get(service)
    assert service_def is not None, f"Service '{service}' not found"

    networks = service_def.get("networks", [])
    assert network in networks, (
        f"Service '{service}' not in network '{network}' (found: {networks})"
    )
    print(f"✅ Service '{service}' in network '{network}'")


@then("docker compose config should succeed")
def docker_compose_config_succeeds(stack: ObservabilityStack) -> None:
    """Assert docker compose config validates without error."""
    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=stack.compose_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"docker compose config failed: {result.stderr}"
    print("✅ docker compose config validates cleanly")


@then(parsers.parse('docker compose config with profile "{profile}" should succeed'))
def docker_compose_config_with_profile_succeeds(
    stack: ObservabilityStack, profile: str
) -> None:
    """Assert docker compose config with specified profile validates."""
    result = subprocess.run(
        ["docker", "compose", "--profile", profile, "config"],
        cwd=stack.compose_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"docker compose config --profile {profile} failed: {result.stderr}"
    )
    print(f"✅ docker compose config --profile {profile} validates cleanly")
