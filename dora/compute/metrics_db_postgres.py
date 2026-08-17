"""Postgres/TimescaleDB-backed metric queries (asyncpg).

Selected via metrics.py when DATABASE_URL points at Postgres
(resource-plan / suite mode). See metrics_db_sqlite.py for the default
self-contained local backend.
"""

import os
from typing import Any


class MetricsDB:
    """Async TimescaleDB connection for metric computation."""

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.environ.get("DATABASE_URL")
        if self.dsn is None:
            raise ValueError("DATABASE_URL must be set or dsn argument provided")
        self.pool = None

    async def connect(self):
        import asyncpg

        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()

    # ── Query builders ─────────────────────────────────────────────────────

    def _window_start(self, window_days: int) -> str:
        return f"NOW() - INTERVAL '{window_days} days'"

    async def deployment_frequency(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Deployment Frequency: deploys/week per team over the window."""
        team_clause = f"AND source = '{team}'" if team and team != "all" else ""
        query = f"""
            SELECT
                source AS team_id,
                COUNT(*)::NUMERIC / GREATEST({window_days} / 7.0, 1.0) AS deploys_per_week
            FROM raw_events
            WHERE event_type = 'deployment'
              AND outcome = 'success'
              AND recorded_at >= {self._window_start(window_days)}
            {team_clause}
            GROUP BY source
            ORDER BY source
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def lead_time(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Lead Time for Changes: P50 and P95 in hours.

        Uses ``metadata->>'first_commit_at'`` as the code committed timestamp.
        Falls back to ``metadata->>'pr_merged_at'`` as a proxy when
        ``first_commit_at`` is not available — the ``proxy_metrics`` flag
        is set to true in this case.

        DORA defers to PR merge time only when first commit is unavailable.
        """
        team_clause = f"AND source = '{team}'" if team and team != "all" else ""

        # We compute two queries:
        # Query A: deployments with first_commit_at (exact, no proxy)
        # Query B: deployments with pr_merged_at but NO first_commit_at (proxy)

        query_a = f"""
            SELECT
                source AS team_id,
                percentile_cont(0.50) WITHIN GROUP (ORDER BY lead_time) AS p50,
                percentile_cont(0.95) WITHIN GROUP (ORDER BY lead_time) AS p95,
                FALSE AS proxy_used
            FROM (
                SELECT
                    source,
                    EXTRACT(EPOCH FROM (
                        (metadata->>'deployed_at')::timestamptz -
                        (metadata->>'first_commit_at')::timestamptz
                    )) / 3600 AS lead_time
                FROM raw_events
                WHERE event_type = 'deployment'
                  AND outcome = 'success'
                  AND metadata ? 'first_commit_at'
                  AND metadata ? 'deployed_at'
                  AND recorded_at >= {self._window_start(window_days)}
                {team_clause}
            ) sub
            GROUP BY source
        """

        query_b = f"""
            SELECT
                source AS team_id,
                percentile_cont(0.50) WITHIN GROUP (ORDER BY lead_time) AS p50,
                percentile_cont(0.95) WITHIN GROUP (ORDER BY lead_time) AS p95,
                TRUE AS proxy_used
            FROM (
                SELECT
                    source,
                    EXTRACT(EPOCH FROM (
                        (metadata->>'deployed_at')::timestamptz -
                        (metadata->>'pr_merged_at')::timestamptz
                    )) / 3600 AS lead_time
                FROM raw_events
                WHERE event_type = 'deployment'
                  AND outcome = 'success'
                  AND NOT (metadata ? 'first_commit_at')
                  AND metadata ? 'pr_merged_at'
                  AND metadata ? 'deployed_at'
                  AND recorded_at >= {self._window_start(window_days)}
                {team_clause}
            ) sub
            GROUP BY source
        """

        async with self.pool.acquire() as conn:
            rows_a = await conn.fetch(query_a)
            rows_b = await conn.fetch(query_b)
            result = {}
            for r in rows_a:
                d = dict(r)
                d["proxy_metrics"] = False
                result[d["team_id"]] = d
            for r in rows_b:
                d = dict(r)
                d["proxy_metrics"] = True
                if d["team_id"] in result:
                    # Merge: combine exact + proxy data
                    existing = result[d["team_id"]]
                    # Use proxy to fill null p50/p95 from query_a
                    if existing.get("p50") is None and d.get("p50") is not None:
                        existing["p50"] = d["p50"]
                        existing["proxy_metrics"] = True
                    if existing.get("p95") is None and d.get("p95") is not None:
                        existing["p95"] = d["p95"]
                else:
                    result[d["team_id"]] = d
            return list(result.values())

    async def fdrt(self, window_days: int, team: str | None) -> list[dict[str, Any]]:
        """Failure Deployment Recovery Time (FDRT).

        DORA 2025 reclassification: FDRT is the time between a failed deployment
        and the next successful deployment of the SAME service (team).
        This is a deployment-gap metric, NOT an incident-resolution metric.

        Citations:
          - DORA State of DevOps Report 2025, "Throughput" chapter:
            "FDRT measures the time from a failed deployment to the next
             successful deployment of the same service, reflecting the team's
             ability to recover from deployment failures."

        Returns null fdrt for teams that have no recovery in the window.
        """
        team_clause = f"AND source = '{team}'" if team and team != "all" else ""

        query = f"""
            WITH ordered_deployments AS (
                SELECT
                    source AS team_id,
                    outcome,
                    recorded_at,
                    LEAD(recorded_at) OVER (
                        PARTITION BY source
                        ORDER BY recorded_at
                    ) AS next_deploy_at
                FROM raw_events
                WHERE event_type = 'deployment'
                  AND recorded_at >= {self._window_start(window_days)}
                {team_clause}
            ),
            fdrt_gaps AS (
                SELECT
                    team_id,
                    EXTRACT(EPOCH FROM (next_deploy_at - recorded_at)) / 3600 AS gap_hours
                FROM ordered_deployments
                WHERE outcome IN ('failure', 'rollback')
                  AND next_deploy_at IS NOT NULL
                  AND (
                      -- Ensure the recovery was a success
                      EXISTS (
                          SELECT 1 FROM raw_events r2
                          WHERE r2.event_type = 'deployment'
                            AND r2.source = ordered_deployments.team_id
                            AND r2.outcome = 'success'
                            AND r2.recorded_at = ordered_deployments.next_deploy_at
                      )
                  )
            )
            SELECT
                team_id,
                percentile_cont(0.50) WITHIN GROUP (ORDER BY gap_hours) AS p50_fdrt_hours
            FROM fdrt_gaps
            GROUP BY team_id
            ORDER BY team_id
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def change_failure_rate(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Change Failure Rate: % of deployments that fail or rollback."""
        team_clause = f"AND source = '{team}'" if team and team != "all" else ""
        query = f"""
            SELECT
                source AS team_id,
                COUNT(*) FILTER (WHERE outcome IN ('failure', 'rollback')) * 1.0
                    / NULLIF(COUNT(*), 0) AS cfr
            FROM raw_events
            WHERE event_type = 'deployment'
              AND recorded_at >= {self._window_start(window_days)}
            {team_clause}
            GROUP BY source
            ORDER BY source
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def rework_rate(
        self, window_days: int, team: str | None
    ) -> list[dict[str, Any]]:
        """Rework Rate: user-visible rework events / total deployments.

        Only counts rework events where ``user_visible`` is true — hotfixes
        for internal issues (false) are excluded per DORA 2025 guidance.
        """
        team_clause = ""
        if team and team != "all":
            team_clause = f"AND d.source = '{team}'"

        query = f"""
            SELECT
                d.source AS team_id,
                COUNT(DISTINCT r.id) * 1.0
                    / NULLIF(COUNT(DISTINCT d.id), 0) AS rework_pct
            FROM raw_events d
            LEFT JOIN raw_events r
                ON r.event_type = 'rework'
                AND r.source = d.source
                AND r.metadata->>'deployment_sha' = d.metadata->>'commit_sha'
                AND (r.metadata->>'user_visible')::boolean = TRUE
                AND r.recorded_at >= {self._window_start(window_days)}
            WHERE d.event_type = 'deployment'
              AND d.recorded_at >= {self._window_start(window_days)}
            {team_clause}
            GROUP BY d.source
            ORDER BY d.source
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def write_snapshot(self, record: dict[str, Any], window_start, window_end):
        """Write one team's metric record to the dora_snapshots hypertable."""
        await self.pool.execute(
            """
            INSERT INTO dora_snapshots
                (team_id, deployment_frequency, lead_time_hours,
                 change_failure_rate, time_to_restore_hours,
                 fdrt_hours, rework_rate_pct, proxy_metrics, dora_tier,
                 snapshot_window_start, snapshot_window_end, recorded_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
            """,
            record["team_id"],
            record.get("deployment_frequency", 0),
            record.get("lead_time_p50_hours"),
            record.get("change_failure_rate"),
            None,  # time_to_restore_hours — deprecated in favor of fdrt
            record.get("fdrt_p50_hours"),
            record.get("rework_rate_pct"),
            record.get("proxy_metrics", False),
            record.get("dora_tier_deployment_frequency", "unknown"),
            window_start,
            window_end,
        )
