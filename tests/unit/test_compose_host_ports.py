"""Host ports that collide on a shared Docker host are configurable, with today's defaults.

Reads compose.yaml statically; no running stack required.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPOSE = yaml.safe_load((ROOT / "compose.yaml").read_text())
ENV_EXAMPLE = (ROOT / ".env.example").read_text()

# service -> (container port, env var, default host port)
CONFIGURABLE = {
    "grafana": ("3000", "GRAFANA_PORT", "3000"),
    "telemetry-generator": ("5000", "TELEMETRY_GENERATOR_PORT", "5001"),
}


@pytest.mark.unit
@pytest.mark.parametrize("service", sorted(CONFIGURABLE))
def test_host_port_is_env_configurable_with_todays_default(service):
    container_port, var, default = CONFIGURABLE[service]
    published = {}
    for spec in COMPOSE["services"][service]["ports"]:
        host, container = str(spec).rsplit(":", 1)
        published[container] = host
    assert published[container_port] == f"${{{var}:-{default}}}"


@pytest.mark.unit
def test_env_example_documents_every_port_variable():
    for _, var, default in CONFIGURABLE.values():
        assert f"{var}={default}" in ENV_EXAMPLE, var
