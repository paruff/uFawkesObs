"""Unit tests for compute/metrics_db_sqlite.py.

Covers the SQLite-backed MetricsDB implementation used by default in the
``dora`` profile. Verifies the same metric math as the Postgres backend
(test_dora_metrics_postgres.py) — deployment frequency, lead time (exact
and proxy), FDRT, change failure rate, and rework rate — reimplemented in
Python since SQLite has no percentile_cont/LEAD() window functions.
"""

import json
from datetime import UTC, datetime, timedelta

import pytest

from dora.compute.metrics_db_sqlite import MetricsDB, _percentile_cont

pytestmark = pytest.mark.asyncio


async def _db():
    db = MetricsDB(dsn="sqlite://:memory:")
    await db.connect()
    return db


async def _insert(db, event_type, source, outcome, metadata=None, hours_ago=0):
    recorded_at = (
        datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours_ago)
    ).isoformat(" ")
    await db.conn.execute(
        "INSERT INTO raw_events (event_type, source, outcome, metadata, recorded_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            event_type,
            source,
            outcome,
            json.dumps(metadata) if metadata else None,
            recorded_at,
        ),
    )
    await db.conn.commit()


class TestPercentileCont:
    def test_single_value(self):
        assert _percentile_cont([5.0], 0.50) == 5.0

    def test_empty_returns_none(self):
        assert _percentile_cont([], 0.50) is None

    def test_interpolates_like_postgres(self):
        # p50 of [1, 2, 3, 4] -> rank = 0.5*3 = 1.5 -> interpolate 2..3 -> 2.5
        assert _percentile_cont([1.0, 2.0, 3.0, 4.0], 0.50) == 2.5


class TestDeploymentFrequency:
    async def test_counts_success_only(self):
        db = await _db()
        await _insert(db, "deployment", "a", "success")
        await _insert(db, "deployment", "a", "success")
        await _insert(db, "deployment", "a", "failure")

        result = await db.deployment_frequency(window_days=7, team=None)

        assert result == [{"team_id": "a", "deploys_per_week": 2.0}]

    async def test_multiple_teams_sorted(self):
        db = await _db()
        await _insert(db, "deployment", "b", "success")
        await _insert(db, "deployment", "a", "success")

        result = await db.deployment_frequency(window_days=7, team=None)

        assert [r["team_id"] for r in result] == ["a", "b"]

    async def test_team_filter(self):
        db = await _db()
        await _insert(db, "deployment", "a", "success")
        await _insert(db, "deployment", "b", "success")

        result = await db.deployment_frequency(window_days=7, team="a")

        assert result == [{"team_id": "a", "deploys_per_week": 1.0}]

    async def test_window_scales_weeks(self):
        db = await _db()
        for _ in range(4):
            await _insert(db, "deployment", "a", "success")

        result = await db.deployment_frequency(window_days=28, team=None)

        assert result == [{"team_id": "a", "deploys_per_week": 1.0}]


class TestLeadTime:
    async def test_exact_from_first_commit_at(self):
        db = await _db()
        await _insert(
            db,
            "deployment",
            "a",
            "success",
            metadata={
                "first_commit_at": "2026-01-01T00:00:00Z",
                "deployed_at": "2026-01-01T12:00:00Z",
            },
        )

        result = await db.lead_time(window_days=30, team=None)

        assert result == [
            {"team_id": "a", "p50": 12.0, "p95": 12.0, "proxy_metrics": False}
        ]

    async def test_proxy_fallback_to_pr_merged_at(self):
        db = await _db()
        await _insert(
            db,
            "deployment",
            "a",
            "success",
            metadata={
                "pr_merged_at": "2026-01-01T00:00:00Z",
                "deployed_at": "2026-01-01T06:00:00Z",
            },
        )

        result = await db.lead_time(window_days=30, team=None)

        assert result == [
            {"team_id": "a", "p50": 6.0, "p95": 6.0, "proxy_metrics": True}
        ]

    async def test_missing_timestamps_excluded(self):
        db = await _db()
        await _insert(db, "deployment", "a", "success", metadata={})

        result = await db.lead_time(window_days=30, team=None)

        assert result == []


class TestFDRT:
    async def test_gap_between_failure_and_next_success(self):
        db = await _db()
        await _insert(db, "deployment", "a", "failure", hours_ago=5)
        await _insert(db, "deployment", "a", "success", hours_ago=2)

        result = await db.fdrt(window_days=30, team=None)

        assert result == [{"team_id": "a", "p50_fdrt_hours": pytest.approx(3.0)}]

    async def test_null_when_no_recovery(self):
        db = await _db()
        await _insert(db, "deployment", "a", "failure", hours_ago=5)

        result = await db.fdrt(window_days=30, team=None)

        assert result == []

    async def test_no_gap_when_next_deploy_also_failed(self):
        db = await _db()
        await _insert(db, "deployment", "a", "failure", hours_ago=5)
        await _insert(db, "deployment", "a", "failure", hours_ago=2)

        result = await db.fdrt(window_days=30, team=None)

        assert result == []


class TestChangeFailureRate:
    async def test_computes_ratio(self):
        db = await _db()
        await _insert(db, "deployment", "a", "success")
        await _insert(db, "deployment", "a", "failure")
        await _insert(db, "deployment", "a", "rollback")

        result = await db.change_failure_rate(window_days=30, team=None)

        assert result == [{"team_id": "a", "cfr": pytest.approx(2 / 3)}]


class TestReworkRate:
    async def test_matches_user_visible_rework_by_sha(self):
        db = await _db()
        await _insert(
            db, "deployment", "a", "success", metadata={"commit_sha": "abc123"}
        )
        await _insert(
            db,
            "rework",
            "a",
            "success",
            metadata={"deployment_sha": "abc123", "user_visible": True},
        )

        result = await db.rework_rate(window_days=30, team=None)

        assert result == [{"team_id": "a", "rework_pct": 1.0}]

    async def test_ignores_non_user_visible_rework(self):
        db = await _db()
        await _insert(
            db, "deployment", "a", "success", metadata={"commit_sha": "abc123"}
        )
        await _insert(
            db,
            "rework",
            "a",
            "success",
            metadata={"deployment_sha": "abc123", "user_visible": False},
        )

        result = await db.rework_rate(window_days=30, team=None)

        assert result == [{"team_id": "a", "rework_pct": 0.0}]


class TestWriteSnapshot:
    async def test_round_trips_record_fields(self):
        db = await _db()
        window_end = datetime.now(UTC).replace(tzinfo=None)
        window_start = window_end - timedelta(days=30)
        record = {
            "team_id": "a",
            "deployment_frequency": 3.5,
            "lead_time_p50_hours": 12.0,
            "change_failure_rate": 0.1,
            "fdrt_p50_hours": 2.0,
            "rework_rate_pct": 0.05,
            "proxy_metrics": False,
            "dora_tier_deployment_frequency": "elite",
        }

        await db.write_snapshot(record, window_start, window_end)

        cursor = await db.conn.execute(
            "SELECT team_id, deployment_frequency, lead_time_hours, "
            "change_failure_rate, fdrt_hours, rework_rate_pct, proxy_metrics, "
            "dora_tier FROM dora_snapshots"
        )
        row = await cursor.fetchone()
        assert row == ("a", 3.5, 12.0, 0.1, 2.0, 0.05, 0, "elite")
