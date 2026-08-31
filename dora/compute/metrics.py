"""uFawkesDORA DORA Metrics Computation.

Computes all five DORA delivery metrics from the raw_events table and
writes results to dora_snapshots + Prometheus pushgateway.

Metrics (DORA 2025):
  - Deployment Frequency (deploys/week)
  - Lead Time for Changes (P50/P95 hours)
  - FDRT — Failure Deployment Recovery Time (deployment-gap, not incident MTTR)
  - Change Failure Rate (% of deployments that fail or rollback)
  - Rework Rate (user-visible rework deployments / total deployments)

DORA 2025 classification:
  - FDRT moves from Stability to Throughput
  - Rework Rate added as Stability metric
  - FDRT is deployment-gap, NOT incident-resolution gap

Usage:
    python compute/metrics.py --window 30 --team paruff/uFawkesObs
    python compute/metrics.py --window 90 --pushgateway http://localhost:9091
    python compute/metrics.py --window 7 --team all --verbose
"""

import argparse
import asyncio
import base64
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from .metrics_db_sqlite import MetricsDB

logger = logging.getLogger("ufawkesdora.metrics")

# DORA 2025 tier thresholds
# Source: DORA State of DevOps Report 2025
TIER_THRESHOLDS = {
    "deployment_frequency": {
        "elite": (lambda v: v >= 7.0),  # Multiple deploys/day = 7+/week
        "high": (lambda v: 1.0 <= v < 7.0),  # Daily to weekly
        "medium": (lambda v: 0.25 <= v < 1.0),  # Weekly to monthly = ~1/month
        "low": (lambda v: v < 0.25),  # Less than monthly (~1/quarter = 0.08)
    },
    "lead_time": {
        "elite": (lambda v: v <= 1.0),  # Less than 1 hour
        "high": (lambda v: 1.0 < v <= 24.0),  # 1 day
        "medium": (lambda v: 24.0 < v <= 168.0),  # 1 week
        "low": (lambda v: v > 168.0),  # More than 1 week
    },
    "fdrt": {
        "elite": (lambda v: v <= 1.0),  # Less than 1 hour
        "high": (lambda v: 1.0 < v <= 24.0),  # 1 day
        "medium": (lambda v: 24.0 < v <= 168.0),  # 1 week
        "low": (lambda v: v > 168.0),  # More than 1 week
    },
    "cfr": {
        "elite": (lambda v: v <= 0.05),  # <= 5%
        "high": (lambda v: 0.05 < v <= 0.10),  # 10%
        "medium": (lambda v: 0.10 < v <= 0.15),  # 15%
        "low": (lambda v: v > 0.15),  # > 15%
    },
    "rework_rate": {
        "elite": (lambda v: v <= 0.05),  # <= 5%
        "high": (lambda v: 0.05 < v <= 0.10),  # 10%
        "medium": (lambda v: 0.10 < v <= 0.15),  # 15%
        "low": (lambda v: v > 0.15),  # > 15%
    },
}

DORA_TIERS = ["elite", "high", "medium", "low"]


def classify_tier(metric_name: str, value: float | None) -> str:
    """Classify a metric value into a DORA 2025 tier.

    Args:
        metric_name: One of ``deployment_frequency``, ``lead_time``,
            ``fdrt``, ``cfr``, ``rework_rate``.
        value: The metric value, or None.

    Returns:
        One of ``elite``, ``high``, ``medium``, ``low``, ``unknown``.
    """
    if value is None:
        return "unknown"
    thresholds = TIER_THRESHOLDS.get(metric_name)
    if not thresholds:
        return "unknown"
    for tier in DORA_TIERS:
        if thresholds[tier](value):
            return tier
    return "unknown"


# ── Metric computation orchestrator ────────────────────────────────────────────


async def compute_all_metrics(
    window_days: int,
    team: str | None = None,
    pushgateway: str | None = None,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """Compute all DORA metrics and write results.

    Args:
        window_days: Number of days to look back.
        team: Team/repo filter. ``None`` or ``"all"`` for all teams.
        pushgateway: Prometheus pushgateway URL for metric emission.
        verbose: Enable debug logging.

    Returns:
        List of result dicts, one per team.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    logger.info(
        "Computing DORA metrics (window=%d days, team=%s)", window_days, team or "all"
    )

    async with MetricsDB() as db:
        # Run all metric queries in parallel
        df, lt, fdrt_res, cfr, rr = await asyncio.gather(
            db.deployment_frequency(window_days, team),
            db.lead_time(window_days, team),
            db.fdrt(window_days, team),
            db.change_failure_rate(window_days, team),
            db.rework_rate(window_days, team),
        )

    # Merge results by team
    results = _merge_team_results(df, lt, fdrt_res, cfr, rr)

    # Write to dora_snapshots
    async with MetricsDB() as db:
        await _write_snapshots(db, results, window_days)

    # Push to Prometheus pushgateway
    if pushgateway:
        await _push_metrics(results, pushgateway)

    return results


def _ensure_team_entry(
    teams: dict[str, dict], team_id: str, proxy: bool = False
) -> dict:
    """Get or create a team entry, initializing all metric keys to None."""
    all_metric_keys = [
        "deployment_frequency",
        "lead_time_p50_hours",
        "lead_time_p95_hours",
        "fdrt_p50_hours",
        "change_failure_rate",
        "rework_rate_pct",
    ]
    if team_id not in teams:
        entry = {"team_id": team_id, "proxy_metrics": proxy}
        for k in all_metric_keys:
            entry[k] = None
        teams[team_id] = entry
    return teams[team_id]


def _to_float_or_none(value: Any) -> float | None:
    return float(value) if value is not None else None


# (source rows, entry key, row key) for the three metrics whose merge is a
# plain float-or-None copy with no team-level side effects. deployment
# frequency and lead time are handled separately below since they also set
# the proxy_metrics flag.
_SIMPLE_METRIC_MERGES = (
    ("fdrt_p50_hours", "p50_fdrt_hours"),
    ("change_failure_rate", "cfr"),
    ("rework_rate_pct", "rework_pct"),
)

# (tier key, classify_tier() metric name, entry key to read the value from)
_TIER_FIELDS = (
    ("dora_tier_deployment_frequency", "deployment_frequency", "deployment_frequency"),
    ("dora_tier_lead_time", "lead_time", "lead_time_p50_hours"),
    ("dora_tier_fdrt", "fdrt", "fdrt_p50_hours"),
    ("dora_tier_cfr", "cfr", "change_failure_rate"),
    ("dora_tier_rework_rate", "rework_rate", "rework_rate_pct"),
)


def _merge_team_results(
    df: list[dict],
    lt: list[dict],
    fdrt_res: list[dict],
    cfr: list[dict],
    rr: list[dict],
) -> list[dict[str, Any]]:
    """Merge per-team metric results into unified records."""
    teams: dict[str, dict] = {}

    for row in df:
        entry = _ensure_team_entry(teams, row["team_id"])
        entry["deployment_frequency"] = float(row["deploys_per_week"])
        entry["proxy_metrics"] = row.get("proxy_metrics", False)

    for row in lt:
        entry = _ensure_team_entry(
            teams, row["team_id"], proxy=row.get("proxy_used", False)
        )
        entry["lead_time_p50_hours"] = _to_float_or_none(row["p50"])
        entry["lead_time_p95_hours"] = _to_float_or_none(row["p95"])
        if row.get("proxy_used"):
            entry["proxy_metrics"] = True

    for rows, (entry_key, row_key) in zip(
        (fdrt_res, cfr, rr), _SIMPLE_METRIC_MERGES, strict=True
    ):
        for row in rows:
            entry = _ensure_team_entry(teams, row["team_id"])
            entry[entry_key] = _to_float_or_none(row[row_key])

    for entry in teams.values():
        for tier_key, metric_name, value_key in _TIER_FIELDS:
            entry[tier_key] = classify_tier(metric_name, entry.get(value_key))

    return list(teams.values())


async def _write_snapshots(
    db: MetricsDB,
    results: list[dict[str, Any]],
    window_days: int,
):
    """Write metric results to the dora_snapshots table."""
    window_end = datetime.now(UTC)
    window_start = window_end - timedelta(days=window_days)

    for record in results:
        await db.write_snapshot(record, window_start, window_end)


def _escape_label_value(value: str) -> str:
    """Escape a string for use as a Prometheus text-exposition label value.

    Per the exposition format spec, backslash, double-quote, and newline
    must be backslash-escaped. ``team_id`` originates from ingested webhook
    payloads and is therefore untrusted input.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


async def _push_metrics(
    results: list[dict[str, Any]],
    pushgateway_url: str,
):
    """Push DORA metrics to Prometheus pushgateway.

    Each metric gets a separate push with team_id, tier labels.
    """
    import aiohttp

    for record in results:
        tid = record["team_id"]
        tier = record.get("dora_tier_deployment_frequency", "unknown")

        # Build Prometheus text format payload
        lines: list[str] = []

        def gauge(
            name: str,
            value: float | None,
            tier_label: str | None = None,
            _tid: str = tid,
            _lines: list[str] = lines,
        ) -> None:
            if value is None:
                return
            labels = f'team_id="{_escape_label_value(_tid)}"'
            if tier_label:
                labels += f',tier="{_escape_label_value(tier_label)}"'
            _lines.append(f"# HELP {name} DORA metric")
            _lines.append(f"# TYPE {name} gauge")
            _lines.append(f"{name}{{{labels}}} {value}")

        gauge(
            "dora_deployment_frequency_per_week",
            record.get("deployment_frequency"),
            tier,
        )
        gauge(
            "dora_lead_time_p50_hours",
            record.get("lead_time_p50_hours"),
            record.get("dora_tier_lead_time"),
        )
        gauge("dora_lead_time_p95_hours", record.get("lead_time_p95_hours"))
        gauge(
            "dora_fdrt_p50_hours",
            record.get("fdrt_p50_hours"),
            record.get("dora_tier_fdrt"),
        )
        gauge(
            "dora_cfr_pct",
            record.get("change_failure_rate"),
            record.get("dora_tier_cfr"),
        )
        gauge(
            "dora_rework_rate_pct",
            record.get("rework_rate_pct"),
            record.get("dora_tier_rework_rate"),
        )

        payload = "\n".join(lines) + "\n"
        job_name = f"ufawkesdora_{tid}"
        # Pushgateway's HTTP router decodes %2F back to a literal '/' before
        # parsing the URL path into job/grouping-key segments, so a plain
        # percent-encoded job name (as urllib.parse.quote produces) breaks
        # on any team_id containing '/' — i.e. every real "org/repo" value —
        # with HTTP 400 ("odd number of components in label string").
        # Pushgateway's own fix for this is the documented job@base64/<val>
        # path convention: https://github.com/prometheus/pushgateway#url
        job_name_b64 = base64.urlsafe_b64encode(job_name.encode()).decode().rstrip("=")

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{pushgateway_url.rstrip('/')}/metrics/job@base64/{job_name_b64}"
                async with session.put(url, data=payload) as resp:
                    if resp.status not in (200, 202):
                        logger.warning(
                            "Pushgateway returned %d for %s", resp.status, job_name
                        )
                    else:
                        logger.debug("Pushed metrics for %s", tid)
        except Exception as e:
            logger.warning("Failed to push metrics for %s: %s", tid, e)


# ── CLI ────────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute DORA delivery metrics from PostgreSQL/TimescaleDB",
    )
    parser.add_argument(
        "--window",
        "-w",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    parser.add_argument(
        "--team",
        "-t",
        default=None,
        help="Team/repo filter (default: all teams)",
    )
    parser.add_argument(
        "--pushgateway",
        "-p",
        default=None,
        help="Prometheus pushgateway URL (e.g. http://localhost:9091)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (default: table format)",
    )
    return parser.parse_args(argv)


async def main_async(args: argparse.Namespace):
    results = await compute_all_metrics(
        window_days=args.window,
        team=args.team,
        pushgateway=args.pushgateway,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        _print_table(results)


def _print_table(results: list[dict]):
    """Pretty-print metrics as a table."""
    if not results:
        print("No results found.")
        return

    header = (
        f"{'Team':<30} {'DF/week':<10} {'LT P50h':<10} {'LT P95h':<10} "
        f"{'FDRT P50h':<10} {'CFR %':<10} {'Rework %':<10} {'Tier':<12}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        df = (
            f"{r.get('deployment_frequency', 0):.2f}"
            if r.get("deployment_frequency") is not None
            else "N/A"
        )
        lt_p50 = (
            f"{r.get('lead_time_p50_hours', 0):.1f}"
            if r.get("lead_time_p50_hours") is not None
            else "N/A"
        )
        lt_p95 = (
            f"{r.get('lead_time_p95_hours', 0):.1f}"
            if r.get("lead_time_p95_hours") is not None
            else "N/A"
        )
        fdrt = (
            f"{r.get('fdrt_p50_hours', 0):.1f}"
            if r.get("fdrt_p50_hours") is not None
            else "N/A"
        )
        cfr = (
            f"{r.get('change_failure_rate', 0) * 100:.1f}"
            if r.get("change_failure_rate") is not None
            else "N/A"
        )
        rr = (
            f"{r.get('rework_rate_pct', 0) * 100:.1f}"
            if r.get("rework_rate_pct") is not None
            else "N/A"
        )
        tier = r.get("dora_tier_deployment_frequency", "N/A")
        print(
            f"{r['team_id']:<30} {df:<10} {lt_p50:<10} {lt_p95:<10} "
            f"{fdrt:<10} {cfr:<10} {rr:<10} {tier:<12}"
        )


def main():
    """CLI entrypoint."""
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
