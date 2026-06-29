"""
Pytest configuration and shared fixtures for Gherkin/BDD acceptance tests.

These fixtures provide the foundational building blocks used across
all .feature files and step definitions. Steps that are reused across
features are imported here so pytest-bdd can discover them; feature-
specific steps live in their own modules under steps/.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import yaml
import pytest

# ---------------------------------------------------------------------------
# Register step definition modules as pytest plugins.
#
# pytest-bdd v8.x registers steps as pytest fixtures in the calling module's
# namespace. For pytest to discover these fixtures, the modules must be
# registered as pytest plugins (or be conftest.py files). The pytest_plugins
# mechanism causes pytest to treat these modules as plugins, scanning them
# for fixtures (including those dynamically injected by the @given/@when/@then
# decorators).
# ---------------------------------------------------------------------------
pytest_plugins = [
    "tests.acceptance.steps.shared_steps",
    "tests.acceptance.steps.adr_docs_steps",
    "tests.acceptance.steps.grafana_dashboard_steps",
]


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root() -> Path:
    """Absolute path to the repo root."""
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def config_dir(project_root: Path) -> Path:
    """Path to config/ directory."""
    return project_root / "config"


@pytest.fixture
def docs_dir(project_root: Path) -> Path:
    """Path to docs/ directory."""
    return project_root / "docs"


@pytest.fixture
def dashboards_dir(project_root: Path) -> Path:
    """Path to dashboards/ directory."""
    return project_root / "dashboards"


@pytest.fixture
def gh_dir(project_root: Path) -> Path:
    """Path to .github/ directory."""
    return project_root / ".github"


@pytest.fixture
def adr_dir(docs_dir: Path) -> Path:
    """Path to docs/adr/ directory."""
    return docs_dir / "adr"


@pytest.fixture
def prometheus_rules_dir(config_dir: Path) -> Path:
    """Path to config/prometheus/rules/ directory."""
    return config_dir / "prometheus" / "rules"


@pytest.fixture
def otel_config_path(config_dir: Path) -> Path:
    """Path to the OTel Collector config file."""
    return config_dir / "otel" / "collector.yaml"


@pytest.fixture
def prometheus_config_path(config_dir: Path) -> Path:
    """Path to the Prometheus config file."""
    return config_dir / "prometheus" / "prometheus.yaml"


@pytest.fixture
def grafana_datasources_path(config_dir: Path) -> Path:
    """Path to the Grafana datasources provisioning file."""
    return config_dir / "grafana" / "provisioning" / "datasources" / "datasources.yaml"


# ---------------------------------------------------------------------------
# YAML loading helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def load_yaml():
    """Provide a helper function to safely load a YAML file."""

    def _load(path: Path):
        text = path.read_text(encoding="utf-8")
        return yaml.safe_load(text)

    return _load


@pytest.fixture
def compose_data(project_root: Path, load_yaml):
    """Parsed compose.yaml as a dictionary."""
    return load_yaml(project_root / "compose.yaml")


# ---------------------------------------------------------------------------
# JSON loading helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def load_json():
    """Provide a helper function to load a JSON file."""

    def _load(path: Path):
        text = path.read_text(encoding="utf-8")
        return json.loads(text)

    return _load


# ---------------------------------------------------------------------------
# Service version extraction from compose.yaml
# ---------------------------------------------------------------------------


@pytest.fixture
def service_image_versions(compose_data: dict) -> dict:
    """
    Map of service name → pinned image tag from compose.yaml.
    Only includes services that use an external image (not build:).
    """
    versions: dict[str, str] = {}
    for name, svc in compose_data.get("services", {}).items():
        image = svc.get("image", "")
        if image:
            # e.g. "prom/prometheus:v3.5.4" → "prom/prometheus:v3.5.4"
            versions[name] = image
    return versions


# ---------------------------------------------------------------------------
# OTel Collector config helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def otel_config(otel_config_path: Path, load_yaml) -> dict:
    """Parsed OTel Collector configuration."""
    return load_yaml(otel_config_path)


@pytest.fixture
def otel_pipelines(otel_config: dict) -> dict:
    """Map of pipeline name → pipeline definition from OTel Collector config."""
    pipelines = otel_config.get("pipelines", {})
    # Handle nested under 'service:' key
    if not pipelines:
        service = otel_config.get("service", {})
        pipelines = service.get("pipelines", {})
    return pipelines


# ---------------------------------------------------------------------------
# Prometheus rules helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def all_prometheus_rules(prometheus_rules_dir: Path, load_yaml) -> list[dict]:
    """
    Load all Prometheus rule files from config/prometheus/rules/ and
    return a flat list of rule groups, each with a '_source_file' key.
    """
    if not prometheus_rules_dir.is_dir():
        return []

    groups: list[dict] = []
    for yml_file in sorted(prometheus_rules_dir.glob("*.yml")):
        data = load_yaml(yml_file)
        if data and "groups" in data:
            for group in data["groups"]:
                group["_source_file"] = yml_file.name
                groups.append(group)
    return groups


# ---------------------------------------------------------------------------
# Prometheus rules helper: check for `or vector(0)` guard
# ---------------------------------------------------------------------------


@pytest.fixture
def check_vector_zero_guard():
    """
    Return a function that checks whether a PromQL expression contains
    an `or vector(0)` guard (accounting for multiline expressions).
    """

    def _check(expr: str) -> bool:
        # Normalise whitespace
        normalised = re.sub(r"\s+", " ", expr.strip())
        return "or vector(0)" in normalised

    return _check


# ---------------------------------------------------------------------------
# Docker Compose config validation
# ---------------------------------------------------------------------------


@pytest.fixture
def docker_compose_config_valid(project_root: Path) -> callable:
    """
    Return a function that validates a docker compose config (with optional
    profile) by running `docker compose config` and checking exit code.

    If Docker CLI is not available, the validation function returns False
    and the calling test should skip or adapt accordingly.
    """

    def _validate(profile: str = "") -> bool:
        if not shutil.which("docker"):
            pytest.skip("Docker CLI not available in this environment")
            return False
        cmd = ["docker", "compose"]
        if profile:
            cmd += ["--profile", profile]
        cmd += ["config", "-q"]
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0

    return _validate


# ---------------------------------------------------------------------------
# Grafana dashboard JSON helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def find_dashboard_json(dashboards_dir: Path, load_json) -> callable:
    """
    Return a function that finds and loads a Grafana dashboard JSON file
    by searching dashboards/ recursively for a file whose .json contents
    contain the given uid.
    """

    def _find(uid: str) -> dict | None:
        for json_file in dashboards_dir.rglob("*.json"):
            try:
                data = load_json(json_file)
                if data.get("uid") == uid:
                    return data
            except (json.JSONDecodeError, KeyError):
                continue
        return None

    return _find


@pytest.fixture
def all_dashboard_jsons(dashboards_dir: Path, load_json) -> list[dict]:
    """
    Load all dashboard JSON files from dashboards/ and return
    a list of parsed dictionaries.
    """
    dashboards: list[dict] = []
    if not dashboards_dir.is_dir():
        return dashboards
    for json_file in sorted(dashboards_dir.rglob("*.json")):
        try:
            data = load_json(json_file)
            dashboards.append(
                {"_source_file": json_file.relative_to(dashboards_dir), **data}
            )
        except json.JSONDecodeError:
            continue
    return dashboards
