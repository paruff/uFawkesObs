"""SQLite-backed metric queries (aiosqlite).

The only backend for the ``dora`` profile — self-contained, zero external
dependencies. SQLite has no percentile_cont/LEAD() OVER window functions,
so this module fetches the raw rows and reimplements the same math in
Python, matching the semantics of those SQL functions.
"""

import json
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    event_queue_id      INTEGER,
    event_type          TEXT    NOT NULL,
    source              TEXT    NOT NULL,
    outcome             TEXT    NOT NULL,
    duration_seconds    INTEGER,
    metadata            TEXT,
    recorded_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dora_snapshots (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id                 TEXT NOT NULL,
    deployment_frequency    REAL,
    lead_time_hours         REAL,
    change_failure_rate     REAL,
    time_to_restore_hours   REAL,
    fdrt_hours              REAL,
    rework_rate_pct         REAL,
    proxy_metrics           BOOLEAN NOT NULL DEFAULT 0,
    dora_tier               TEXT,
    snapshot_window_start   TIMESTAMP,
    snapshot_window_end     TIMESTAMP,
    recorded_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def _percentile_cont(values: list[float], p: float) -> float | None:
    """Postgres percentile_cont(p) WITHIN GROUP (ORDER BY x): linear interpolation."""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = p * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (rank - lo) * (s[hi] - s[lo])


def _sqlite_path(dsn: str) -> str:
    """Translate a sqlite:// DSN into a path aiosqlite understands."""
    if dsn in ("sqlite://:memory:", ":memory:"):
        return ":memory:"
    if dsn.startswith("sqlite:////"):
        return dsn[len("sqlite:///") :]
    if dsn.startswith("sqlite:///"):
        return dsn[len("sqlite:///") :]
    if dsn.startswith("sqlite://"):
        return dsn[len("sqlite://") :]
    return dsn


class MetricsDB:
    """Async SQLite connection for metric computation."""

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.environ.get("DATABASE_URL")
        if self.dsn is None:
            raise ValueError("DATABASE_URL must be set or dsn argument provided")
        self.conn: aiosqlite.Connection | None = None

    async def connect(self):
        self.conn = await aiosqlite.connect(_sqlite_path(self.dsn))
        await self.conn.executescript(_SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()

    # ── Row fetch helpers ───────────────────────────────────────────────────

    def _cutoff(self, window_days: int) -> str:
        cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=window_days)
        return cutoff.isoformat(" ")

    async def _deployment_rows(
        self,
        window_days: int,
        team: str | None,
        outcomes: tuple[str, ...] | None = None,
    ) -> list[tuple]:
        """Fetch (source, outcome, recorded_at, metadata) for deployment events."""
        sql = (
            "SELECT source, outcome, recorded_at, metadata FROM raw_events "
            "WHERE event_type = 'deployment' AND recorded_at >= ?"
        )
        params: list[Any] = [self._cutoff(window_days)]
        if outcomes:
            sql += f" AND outcome IN ({','.join('?' * len(outcomes))})"
            params.extend(outcomes)
        if team and team != "all":
            sql += " AND source = ?"
            params.append(team)
        cursor = await self.conn.execute(sql, params)
        return await cursor.fetchall()

    # ── Metric queries ──────────────────────────────────────────────────────

    async def deployment_frequency(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Deployment Frequency: deploys/week per team over the window."""
        rows = await self._deployment_rows(window_days, team, outcomes=("success",))
        counts: dict[str, int] = {}
        for source, *_ in rows:
            counts[source] = counts.get(source, 0) + 1
        weeks = max(window_days / 7.0, 1.0)
        return [
            {"team_id": source, "deploys_per_week": count / weeks}
            for source, count in sorted(counts.items())
        ]

    async def lead_time(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Lead Time for Changes: P50 and P95 in hours.

        Uses ``first_commit_at`` when present, falls back to
        ``pr_merged_at`` (proxy metric).
        """
        rows = await self._deployment_rows(window_days, team, outcomes=("success",))
        exact: dict[str, list[float]] = {}
        proxy: dict[str, list[float]] = {}
        for source, _outcome, _recorded_at, metadata in rows:
            meta = json.loads(metadata) if metadata else {}
            deployed_at = meta.get("deployed_at")
            if not deployed_at:
                continue
            deployed = datetime.fromisoformat(deployed_at.replace("Z", "+00:00"))
            if meta.get("first_commit_at"):
                started = datetime.fromisoformat(
                    meta["first_commit_at"].replace("Z", "+00:00")
                )
                exact.setdefault(source, []).append(
                    (deployed - started).total_seconds() / 3600
                )
            elif meta.get("pr_merged_at"):
                started = datetime.fromisoformat(
                    meta["pr_merged_at"].replace("Z", "+00:00")
                )
                proxy.setdefault(source, []).append(
                    (deployed - started).total_seconds() / 3600
                )

        result: dict[str, dict[str, Any]] = {}
        for source, values in exact.items():
            result[source] = {
                "team_id": source,
                "p50": _percentile_cont(values, 0.50),
                "p95": _percentile_cont(values, 0.95),
                "proxy_metrics": False,
            }
        for source, values in proxy.items():
            p50, p95 = _percentile_cont(values, 0.50), _percentile_cont(values, 0.95)
            if source in result:
                existing = result[source]
                if existing["p50"] is None and p50 is not None:
                    existing["p50"] = p50
                    existing["proxy_metrics"] = True
                if existing["p95"] is None and p95 is not None:
                    existing["p95"] = p95
            else:
                result[source] = {
                    "team_id": source,
                    "p50": p50,
                    "p95": p95,
                    "proxy_metrics": True,
                }
        return list(result.values())

    async def fdrt(self, window_days: int, team: str | None) -> list[dict[str, Any]]:
        """Failure Deployment Recovery Time: gap from a failed deploy to the
        next deploy of the same source, when that next deploy succeeded.

        ponytail: matches the next row directly rather than Postgres's
        recorded_at self-join, which is equivalent unless two deployments of
        the same source share an identical recorded_at timestamp.
        """
        rows = await self._deployment_rows(window_days, team)
        by_source: dict[str, list[tuple[str, str]]] = {}
        for source, outcome, recorded_at, _metadata in rows:
            by_source.setdefault(source, []).append((outcome, recorded_at))

        gaps: dict[str, list[float]] = {}
        for source, events in by_source.items():
            events.sort(key=lambda e: e[1])
            for i, (outcome, recorded_at) in enumerate(events[:-1]):
                if outcome not in ("failure", "rollback"):
                    continue
                next_outcome, next_recorded_at = events[i + 1]
                if next_outcome != "success":
                    continue
                gap_hours = (
                    datetime.fromisoformat(next_recorded_at)
                    - datetime.fromisoformat(recorded_at)
                ).total_seconds() / 3600
                gaps.setdefault(source, []).append(gap_hours)

        return [
            {"team_id": source, "p50_fdrt_hours": _percentile_cont(values, 0.50)}
            for source, values in sorted(gaps.items())
        ]

    async def change_failure_rate(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Change Failure Rate: % of deployments that fail or rollback."""
        rows = await self._deployment_rows(window_days, team)
        totals: dict[str, int] = {}
        failures: dict[str, int] = {}
        for source, outcome, _recorded_at, _metadata in rows:
            totals[source] = totals.get(source, 0) + 1
            if outcome in ("failure", "rollback"):
                failures[source] = failures.get(source, 0) + 1
        return [
            {"team_id": source, "cfr": failures.get(source, 0) / total}
            for source, total in sorted(totals.items())
        ]

    async def rework_rate(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Rework Rate: user-visible rework events / total deployments.

        Matches a rework event to a deployment when they share a source and
        ``rework.metadata.deployment_sha == deployment.metadata.commit_sha``.
        """
        deploy_rows = await self._deployment_rows(window_days, team)
        cursor = await self.conn.execute(
            "SELECT source, metadata FROM raw_events "
            "WHERE event_type = 'rework' AND recorded_at >= ?",
            [self._cutoff(window_days)],
        )
        rework_rows = await cursor.fetchall()

        rework_by_source: dict[str, list[dict]] = {}
        for source, metadata in rework_rows:
            meta = json.loads(metadata) if metadata else {}
            if meta.get("user_visible") is True:
                rework_by_source.setdefault(source, []).append(meta)

        totals: dict[str, int] = {}
        matched: dict[str, int] = {}
        for source, _outcome, _recorded_at, metadata in deploy_rows:
            totals[source] = totals.get(source, 0) + 1
            meta = json.loads(metadata) if metadata else {}
            commit_sha = meta.get("commit_sha")
            if commit_sha and any(
                r.get("deployment_sha") == commit_sha
                for r in rework_by_source.get(source, [])
            ):
                matched[source] = matched.get(source, 0) + 1

        return [
            {"team_id": source, "rework_pct": matched.get(source, 0) / total}
            for source, total in sorted(totals.items())
        ]

    async def write_snapshot(self, record: dict[str, Any], window_start, window_end):
        """Write one team's metric record to the dora_snapshots table."""
        await self.conn.execute(
            """
            INSERT INTO dora_snapshots
                (team_id, deployment_frequency, lead_time_hours,
                 change_failure_rate, time_to_restore_hours,
                 fdrt_hours, rework_rate_pct, proxy_metrics, dora_tier,
                 snapshot_window_start, snapshot_window_end, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                record["team_id"],
                record.get("deployment_frequency", 0),
                record.get("lead_time_p50_hours"),
                record.get("change_failure_rate"),
                None,  # time_to_restore_hours — deprecated in favor of fdrt
                record.get("fdrt_p50_hours"),
                record.get("rework_rate_pct"),
                record.get("proxy_metrics", False),
                record.get("dora_tier_deployment_frequency", "unknown"),
                window_start.isoformat(" "),
                window_end.isoformat(" "),
            ),
        )
        await self.conn.commit()
