"""The InSpec ports control must understand `${VAR:-default}` in compose.yaml port mappings.

The control compares the running container's bound ports with compose.yaml. A mapping such
as "${GRAFANA_PORT:-3000}:3000" must be expanded the way Compose expands it (the variable
if set and non-empty, otherwise the default) before it is split into IP, host and container
port. Splitting the raw text on ":" breaks on the ":-" inside the expression.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest

LIBRARY = (
    pathlib.Path(__file__).resolve().parents[2]
    / "inspec"
    / "ufawkesobs-conformance"
    / "libraries"
    / "compose_ports.rb"
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(shutil.which("ruby") is None, reason="ruby is not installed"),
]


def parse(mapping: str, env: dict[str, str] | None = None) -> list[str]:
    script = (
        f"require {str(LIBRARY)!r}; require 'json'; "
        f"puts JSON.generate(ComposePorts.parse(ARGV[0], ENV))"
    )
    out = subprocess.run(
        ["ruby", "-e", script, mapping],
        env={"PATH": "/usr/bin:/usr/local/bin:/bin", **(env or {})},
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out)


def test_plain_mapping_is_unchanged():
    assert parse("3000:3000") == ["0.0.0.0", "3000", "3000"]


def test_loopback_mapping_is_unchanged():
    assert parse("127.0.0.1:3200:3200") == ["127.0.0.1", "3200", "3200"]


def test_variable_with_default_uses_the_default_when_unset():
    assert parse("${GRAFANA_PORT:-3000}:3000") == ["0.0.0.0", "3000", "3000"]


def test_variable_with_default_uses_the_variable_when_set():
    assert parse("${GRAFANA_PORT:-3000}:3000", {"GRAFANA_PORT": "3300"}) == [
        "0.0.0.0",
        "3300",
        "3000",
    ]


def test_empty_variable_falls_back_to_the_default_like_compose():
    assert parse("${GRAFANA_PORT:-3000}:3000", {"GRAFANA_PORT": ""}) == [
        "0.0.0.0",
        "3000",
        "3000",
    ]


def test_loopback_with_variable():
    assert parse("127.0.0.1:${DORA_PORT:-8088}:8088") == ["127.0.0.1", "8088", "8088"]
