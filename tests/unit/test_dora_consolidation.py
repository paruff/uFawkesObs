"""Consolidation tests for DORA-CONSOLIDATION-01 (issue #200).

The uFawkesDORA ingestion/compute/events Python packages were moved from the
standalone repo into this one under a new top-level `dora/` directory, and the
`dora-api` compose service volume mount was fixed to point at it.

This suite validates the move statically (no running stack, no external deps):

  - the `dora/` package tree exists with the expected files
  - no stale top-level `ingestion/`, `compute/`, or `events/` directories remain
  - the event JSON schemas in `dora/events/` are valid draft-07 schemas
  - the `dora-api` compose service mounts `./dora/ingestion` and
    `./dora/events` into the container and keeps the `dora` profile contract
  - the moved ingestion code keeps its `ingestion.*` import namespace so the
    container mount at `/app/ingestion` still resolves at runtime

Run:  pytest tests/unit/test_dora_consolidation.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DORA_DIR = REPO_ROOT / "dora"
COMPOSE_PATH = REPO_ROOT / "compose.yaml"

EXPECTED_INGESTION_FILES = [
    "Dockerfile",
    "__init__.py",
    "api/__init__.py",
    "api/main.py",
    "api/queue.py",
    "api/validator.py",
    "processor/__init__.py",
    "processor/worker.py",
    "requirements-ingestion.txt",
]
EXPECTED_COMPUTE_FILES = [
    "__init__.py",
    "metrics.py",
    "requirements.txt",
]
EXPECTED_EVENT_SCHEMAS = [
    "deployment-event.schema.json",
    "incident-event.schema.json",
    "pr-event.schema.json",
    "rework-event.schema.json",
]

# event_type const -> schema filename (must match validator.EVENT_TYPE_SCHEMA_MAP)
EVENT_TYPE_BY_SCHEMA = {
    "deployment-event.schema.json": "deployment",
    "incident-event.schema.json": "incident",
    "pr-event.schema.json": "pr",
    "rework-event.schema.json": "rework",
}


@pytest.fixture(scope="module")
def compose_data() -> dict:
    """Return the parsed compose.yaml as a dict."""
    if not COMPOSE_PATH.exists():
        pytest.fail(f"compose.yaml not found at {COMPOSE_PATH}")
    with open(COMPOSE_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "compose.yaml must parse to a mapping"
    return data


@pytest.fixture(scope="module")
def dora_api(compose_data: dict) -> dict:
    """Return the dora-api service definition from compose.yaml."""
    services = compose_data.get("services")
    assert services is not None, "compose.yaml has no 'services' key"
    assert "dora-api" in services, "compose.yaml is missing the dora-api service"
    return services["dora-api"]


# ---------------------------------------------------------------------------
# dora/ package layout
# ---------------------------------------------------------------------------
class TestDoraPackageLayout:
    """The uFawkesDORA packages must live under dora/."""

    @pytest.mark.parametrize("rel", EXPECTED_INGESTION_FILES)
    def test_ingestion_file_present(self, rel: str) -> None:
        assert (DORA_DIR / "ingestion" / rel).is_file(), (
            f"expected dora/ingestion/{rel} — move did not land"
        )

    @pytest.mark.parametrize("rel", EXPECTED_COMPUTE_FILES)
    def test_compute_file_present(self, rel: str) -> None:
        assert (DORA_DIR / "compute" / rel).is_file(), (
            f"expected dora/compute/{rel} — move did not land"
        )

    @pytest.mark.parametrize("name", EXPECTED_EVENT_SCHEMAS)
    def test_event_schema_present(self, name: str) -> None:
        assert (DORA_DIR / "events" / name).is_file(), (
            f"expected dora/events/{name} — move did not land"
        )

    @pytest.mark.parametrize("stale", ["ingestion", "compute", "events"])
    def test_no_stale_top_level_dir(self, stale: str) -> None:
        """The packages moved out of the repo root — nothing left behind."""
        assert not (REPO_ROOT / stale).is_dir(), (
            f"stale top-level {stale}/ directory still exists after the move"
        )


# ---------------------------------------------------------------------------
# Event schemas
# ---------------------------------------------------------------------------
class TestDoraEventSchemas:
    """The moved schemas must remain valid, canonical draft-07 documents."""

    def test_all_schemas_parse_and_validate(self) -> None:
        meta_schema = jsonschema.Draft7Validator.META_SCHEMA
        for name in EXPECTED_EVENT_SCHEMAS:
            path = DORA_DIR / "events" / name
            with open(path, encoding="utf-8") as fh:
                schema = json.load(fh)
            validator = jsonschema.Draft7Validator(meta_schema)
            errors = sorted(validator.iter_errors(schema), key=lambda e: list(e.path))
            assert not errors, f"{name} is not a valid draft-07 schema: {errors[0]}"

    @pytest.mark.parametrize(
        "name,expected_type",
        list(EVENT_TYPE_BY_SCHEMA.items()),
        ids=list(EVENT_TYPE_BY_SCHEMA.keys()),
    )
    def test_event_type_const_matches(self, name: str, expected_type: str) -> None:
        with open(DORA_DIR / "events" / name, encoding="utf-8") as fh:
            schema = json.load(fh)
        assert schema.get("properties", {}).get("event_type", {}).get("const") == (
            expected_type
        ), f"{name} event_type const must be '{expected_type}'"

    @pytest.mark.parametrize("name", EXPECTED_EVENT_SCHEMAS)
    def test_required_fields_present(self, name: str) -> None:
        with open(DORA_DIR / "events" / name, encoding="utf-8") as fh:
            schema = json.load(fh)
        required = set(schema.get("required", []))
        assert {"schema_version", "event_type"} <= required, (
            f"{name} must require schema_version and event_type"
        )
        assert required & {"occurred_at", "deployed_at", "triggered_at"}, (
            f"{name} must require a timestamp field "
            "(occurred_at, deployed_at, or triggered_at)"
        )


# ---------------------------------------------------------------------------
# compose.yaml dora-api service
# ---------------------------------------------------------------------------
class TestComposeDoraApi:
    """The dora-api service must mount dora/ and keep the dora profile contract."""

    def test_volume_mounts_dora_ingestion(self, dora_api: dict) -> None:
        volumes = dora_api.get("volumes", [])
        assert "./dora/ingestion:/app/ingestion:ro" in volumes, (
            "dora-api volume mount must be './dora/ingestion:/app/ingestion:ro' — "
            "the ./ingestion: prefix must be fixed per ADR-007"
        )

    def test_volume_mounts_dora_events(self, dora_api: dict) -> None:
        volumes = dora_api.get("volumes", [])
        assert "./dora/events:/app/events:ro" in volumes, (
            "dora-api must mount the moved event schemas into /app/events"
        )

    def test_dora_profile(self, dora_api: dict) -> None:
        assert "dora" in dora_api.get("profiles", []), (
            "dora-api must be gated behind the dora profile"
        )

    def test_healthcheck_defined(self, dora_api: dict) -> None:
        assert "healthcheck" in dora_api, (
            "every service must define a healthcheck (AGENTS.md §4)"
        )

    def test_database_url_defaults_to_sqlite(self, dora_api: dict) -> None:
        env = dora_api.get("environment", [])
        assert "DATABASE_URL=${DATABASE_URL:-sqlite:////data/dora/dora.db}" in env, (
            "dora-api must default DATABASE_URL to the self-contained SQLite path"
        )

    def test_sqlite_volume_mount(self, dora_api: dict) -> None:
        assert "./data/dora:/data/dora" in dora_api.get("volumes", []), (
            "dora-api must mount ./data/dora for the SQLite database file"
        )

    def test_observability_network(self, dora_api: dict) -> None:
        assert "observability" in dora_api.get("networks", {}), (
            "dora-api must join the observability network"
        )

    def test_container_name_matches_otlp_target(self, dora_api: dict) -> None:
        assert dora_api.get("container_name") == "ufawkesdora-ingestion", (
            "container_name must stay ufawkesdora-ingestion — collectors and "
            "docs reference that hostname (the otel-collector-dora container "
            "that formerly targeted it has been removed)"
        )


# ---------------------------------------------------------------------------
# compute + pushgateway fold-in (issue #205 pattern, extended)
# ---------------------------------------------------------------------------
class TestComputeFoldIn:
    """The DORA compute loop runs inside dora-api, and Pushgateway is gone.

    Replaces TestComposeDoraCompute/TestComposePushgateway, which asserted the
    two-container design this consolidation removed. The coverage is kept, not
    dropped: these assert the architecture that replaced it, including guards
    against either service being reintroduced by accident.

    Why the containers went away:
      - dora-compute was a `while true; sleep 3600` wrapper around one Python
        command, writing dora_snapshots to the same SQLite file dora-api writes
        events to. The DB runs in rollback-journal mode, where a writer takes
        an exclusive lock that blocks readers too, so the split guaranteed
        cross-process contention for no isolation benefit on a single node.
      - Pushgateway is documented for ephemeral batch jobs. dora-compute was
        long-running, so pushing cost the `up` liveness signal and left series
        alive after their producer stopped.
    """

    def test_dora_compute_service_removed(self, compose_data: dict) -> None:
        assert "dora-compute" not in compose_data["services"], (
            "dora-compute was folded into dora-api's lifespan; a separate "
            "container reintroduces the dual-writer SQLite contention"
        )

    def test_pushgateway_service_removed(self, compose_data: dict) -> None:
        assert "pushgateway" not in compose_data["services"], (
            "Pushgateway was replaced by Prometheus scraping dora-api:8088"
            "/metrics directly — see config/prometheus/prometheus.yaml"
        )

    def test_lifespan_starts_compute_loop(self) -> None:
        src = (DORA_DIR / "ingestion" / "api" / "main.py").read_text(encoding="utf-8")
        assert "run_compute_loop(shutdown_event)" in src, (
            "dora-api's lifespan must start the compute loop as a background task"
        )

    def test_metrics_endpoint_exposed(self) -> None:
        src = (DORA_DIR / "ingestion" / "api" / "main.py").read_text(encoding="utf-8")
        assert '@app.get("/metrics"' in src, (
            "dora-api must expose /metrics for Prometheus to scrape"
        )

    def test_compute_module_shipped_into_api_image(self) -> None:
        dockerfile = (DORA_DIR / "ingestion" / "Dockerfile").read_text(encoding="utf-8")
        assert "COPY dora/compute/metrics.py" in dockerfile, (
            "the API image must ship the compute module now that the loop "
            "runs in-process"
        )

    def test_compute_env_configured_on_api(self, compose_data: dict) -> None:
        env = compose_data["services"]["dora-api"].get("environment", [])
        joined = " ".join(env)
        assert "DORA_COMPUTE_INTERVAL_SECONDS" in joined
        assert "DORA_COMPUTE_WINDOW_DAYS" in joined


class TestDoraComputeFiles:
    """dora-compute build inputs moved/added for issue #205."""

    EXPECTED_FILES = ["Dockerfile", "run.sh"]

    @pytest.mark.parametrize("rel", EXPECTED_FILES)
    def test_file_present(self, rel: str) -> None:
        assert (DORA_DIR / "compute" / rel).is_file(), (
            f"expected dora/compute/{rel} — issue #205 did not land"
        )


# ---------------------------------------------------------------------------
# dora-api background worker fold-in (issue #205)
# ---------------------------------------------------------------------------
class TestIngestionWorkerFoldIn:
    """The event_queue worker runs as a background task inside dora-api's
    FastAPI lifespan, not a separate container (see ADR-007 amendment)."""

    def test_lifespan_starts_worker_loop(self) -> None:
        src = (DORA_DIR / "ingestion" / "api" / "main.py").read_text(encoding="utf-8")
        assert "from ingestion.processor.worker import run_worker_loop" in src
        assert "run_worker_loop(shutdown_event=shutdown_event)" in src

    def test_lifespan_stops_worker_on_shutdown(self) -> None:
        src = (DORA_DIR / "ingestion" / "api" / "main.py").read_text(encoding="utf-8")
        assert "shutdown_event.set()" in src


# ---------------------------------------------------------------------------
# Container import contract
# ---------------------------------------------------------------------------
class TestIngestionImportContract:
    """The moved code must keep its `ingestion.*` namespace.

    dora-api mounts ./dora/ingestion at /app/ingestion in the container, so the
    modules are importable as `ingestion.api.*`. Renaming them to dora.ingestion.*
    would break the running service — that is issue #205's pyproject scope.
    """

    def test_main_keeps_ingestion_imports(self) -> None:
        src = (DORA_DIR / "ingestion" / "api" / "main.py").read_text(encoding="utf-8")
        assert "from ingestion.api.queue import" in src
        assert "from ingestion.api.validator import" in src
        assert "dora.ingestion" not in src

    def test_dockerfile_builds_ingestion_module(self) -> None:
        dockerfile = (DORA_DIR / "ingestion" / "Dockerfile").read_text(encoding="utf-8")
        assert "ingestion.api.main:app" in dockerfile, (
            "Dockerfile CMD must still target uvicorn ingestion.api.main:app"
        )
