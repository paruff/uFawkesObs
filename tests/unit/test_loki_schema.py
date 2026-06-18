"""
Unit tests that validate Loki config is compatible with Loki 3.x.

Loki 3.x removed BoltDB entirely. These tests assert the config uses
the tsdb storage schema and contains no BoltDB references.

Run:  pytest tests/unit/test_loki_schema.py -v
      (no running Loki required — reads config/loki/loki.yaml statically)

Expected behavior:
  - If loki.yaml uses boltdb: tests FAIL with clear messages (correct)
  - If loki.yaml uses tsdb: tests PASS (correct)
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path to loki.yaml relative to this file's directory
# ---------------------------------------------------------------------------
LOKI_CONFIG_PATH = pathlib.Path(__file__).resolve().parents[2] / "config" / "loki" / "loki.yaml"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def loki_config_raw() -> str:
    """Return the raw text content of loki.yaml (for string searches)."""
    if not LOKI_CONFIG_PATH.exists():
        pytest.fail(f"loki.yaml not found at {LOKI_CONFIG_PATH}")
    return LOKI_CONFIG_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def loki_config() -> dict:
    """Load and return the parsed loki.yaml as a dict."""
    if not LOKI_CONFIG_PATH.exists():
        pytest.fail(f"loki.yaml not found at {LOKI_CONFIG_PATH}")
    with open(LOKI_CONFIG_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "loki.yaml must parse to a mapping"
    return data


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestLokiSchema3x:
    """Validate Loki config is 3.x-compatible (no BoltDB, uses tsdb)."""

    def test_no_boltdb_references(self, loki_config_raw: str) -> None:
        """Assert the file contains NO references to boltdb or boltdb-shipper.

        Loki 3.x removed BoltDB entirely. Any reference means the config
        is incompatible and must be updated before upgrading.
        """
        lower = loki_config_raw.lower()
        violations = []
        if "boltdb-shipper" in lower:
            violations.append("boltdb-shipper")
        if "boltdb" in lower:
            violations.append("boltdb")
        assert not violations, (
            f"loki.yaml contains BoltDB references: {', '.join(violations)}. "
            f"Loki 3.x removed BoltDB entirely — migrate to tsdb storage schema."
        )

    def test_schema_config_exists(self, loki_config: dict) -> None:
        """Assert schema_config.configs exists and is a non-empty list."""
        schema_config = loki_config.get("schema_config")
        assert schema_config is not None, (
            "loki.yaml is missing 'schema_config' key"
        )
        configs = schema_config.get("configs")
        assert configs is not None, (
            "loki.yaml is missing 'schema_config.configs'"
        )
        assert isinstance(configs, list), (
            f"schema_config.configs must be a list, got {type(configs).__name__}"
        )
        assert len(configs) > 0, (
            "schema_config.configs is empty — at least one schema entry is required"
        )

    def test_all_schemas_use_tsdb(self, loki_config: dict) -> None:
        """Assert every entry in schema_config.configs uses store: tsdb.

        Loki 3.x only supports tsdb. BoltDB entries must be removed.
        """
        configs = loki_config.get("schema_config", {}).get("configs", [])
        assert len(configs) > 0, "No schema configs to check"

        for i, entry in enumerate(configs):
            store = entry.get("store")
            assert store == "tsdb", (
                f"schema_config.configs[{i}] has store: '{store}' — "
                f"expected 'tsdb'. Loki 3.x requires tsdb storage schema."
            )

    def test_no_boltdb_shipper_in_storage_config(self, loki_config: dict) -> None:
        """Assert storage_config does not contain a boltdb_shipper key."""
        storage_config = loki_config.get("storage_config")
        assert storage_config is not None, (
            "loki.yaml is missing 'storage_config' key"
        )
        assert "boltdb_shipper" not in storage_config, (
            "storage_config contains 'boltdb_shipper' key — "
            "remove it and use tsdb_shipper for Loki 3.x compatibility."
        )

    def test_delete_request_store_configured(self, loki_config: dict) -> None:
        """Assert compactor.delete-request-store is set when retention is enabled.

        Loki 3.x requires delete-request-store when retention is enabled.
        Missing this field causes a startup error.
        """
        compactor = loki_config.get("compactor")
        assert compactor is not None, (
            "loki.yaml is missing 'compactor' key"
        )
        retention_enabled = compactor.get("retention_enabled", False)
        if retention_enabled:
            delete_store = compactor.get("delete_request_store")
            assert delete_store is not None, (
                "compactor.retention_enabled is true but "
                "compactor.delete_request_store is not set. "
                "Loki 3.x requires delete-request-store when retention is enabled."
            )

    def test_no_shared_store_in_tsdb_shipper(self, loki_config: dict) -> None:
        """Assert tsdb_shipper does not contain the removed shared_store field.

        Loki 3.x removed the shared_store field from indexshipper.Config.
        """
        storage_config = loki_config.get("storage_config", {})
        tsdb_shipper = storage_config.get("tsdb_shipper", {})
        assert "shared_store" not in tsdb_shipper, (
            "storage_config.tsdb_shipper contains 'shared_store' key — "
            "this field was removed in Loki 3.x."
        )
