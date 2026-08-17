"""Unit tests for compute/metrics_db_postgres.py.

Covers the Postgres/asyncpg-backed MetricsDB implementation used when
DATABASE_URL points at Postgres (resource-plane / suite mode). See
test_dora_metrics.py for the backend-agnostic orchestration tests and
test_dora_metrics_sqlite.py for the SQLite backend.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dora.compute.metrics_db_postgres import MetricsDB


# ── Tests: MetricsDB (Postgres) ────────────────────────────────────────────────


class TestMetricsDB:
    """Cover MetricsDB class methods (lines 100-126)."""

    def test_init_with_dsn(self):
        """Line 101-104: __init__ with explicit DSN."""
        db = MetricsDB(dsn="postgresql://localhost/test")
        assert db.dsn == "postgresql://localhost/test"
        assert db.pool is None

    def test_init_without_dsn_uses_env(self):
        """Line 101: __init__ without DSN reads DATABASE_URL env."""
        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgresql://env/test"}, clear=True
        ):
            db = MetricsDB()
        assert db.dsn == "postgresql://env/test"
        assert db.pool is None

    def test_init_without_dsn_no_env_raises(self):
        """Line 102-103: no DSN and no DATABASE_URL raises ValueError."""
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="DATABASE_URL must be set"),
        ):
            MetricsDB()

    def test_window_start_format(self):
        """Line 126: _window_start returns correct SQL fragment."""
        db = MetricsDB(dsn="postgresql://localhost/test")
        result = db._window_start(30)
        assert result == "NOW() - INTERVAL '30 days'"

    @pytest.mark.asyncio
    async def test_connect_creates_pool(self):
        """Lines 107-109: connect() creates asyncpg pool."""
        mock_pool = MagicMock()
        with patch(
            "asyncpg.create_pool", AsyncMock(return_value=mock_pool)
        ) as mock_create:
            db = MetricsDB(dsn="postgresql://localhost/test")
            await db.connect()
        assert db.pool is mock_pool
        mock_create.assert_awaited_once_with(
            "postgresql://localhost/test", min_size=1, max_size=5
        )

    @pytest.mark.asyncio
    async def test_close_with_pool(self):
        """Lines 112-114: close() closes pool and sets to None."""
        mock_pool = MagicMock()
        mock_pool.close = AsyncMock()

        db = MetricsDB(dsn="postgresql://localhost/test")
        db.pool = mock_pool
        await db.close()

        mock_pool.close.assert_awaited_once()
        assert db.pool is None

    @pytest.mark.asyncio
    async def test_close_without_pool(self):
        """Lines 112: close() with pool=None is a no-op."""
        db = MetricsDB(dsn="postgresql://localhost/test")
        await db.close()  # should not raise
        assert db.pool is None

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Lines 117-121: __aenter__ connects, __aexit__ closes."""
        mock_pool = MagicMock()
        mock_pool.close = AsyncMock()
        with patch("asyncpg.create_pool", AsyncMock(return_value=mock_pool)):
            async with MetricsDB(dsn="postgresql://localhost/test") as db:
                assert db.pool is mock_pool
        mock_pool.close.assert_awaited_once()
