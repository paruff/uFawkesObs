#!/usr/bin/env python3
"""Backfill DORA events from merged-PR history (read via `gh`), runner-free.

Each merged PR in the window becomes a `pr` event and a `deployment` event
(merge to main = delivery). Revert PRs become a `rollback` deployment plus a
user-visible `rework` event. Dry-run prints NDJSON; --post sends to dora-api.

  scripts/backfill_dora_from_github.py paruff/uFawkesObs paruff/uFawkes.dev
  DORA_API_KEY=... scripts/backfill_dora_from_github.py --post http://localhost:8088 paruff/x

ponytail: dora-api windows on ingest time (recorded_at), not deployed_at, so
only the last --days are sent and FDRT gaps collapse to ~0 for a backfill.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

FIELDS = "number,title,url,mergedAt,mergeCommit,additions,deletions,commits"


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def events_for(repo: str, prs: list[dict], now: datetime, days: int) -> list[dict]:
    cutoff = now - timedelta(days=days)
    merged = [p for p in prs if p.get("mergedAt") and _ts(p["mergedAt"]) >= cutoff]
    out: list[dict] = []
    for p in sorted(merged, key=lambda p: p["mergedAt"]):
        sha = p["mergeCommit"]["oid"]
        first = min(
            (c["authoredDate"] for c in p.get("commits", [])), default=p["mergedAt"]
        )
        is_revert = p["title"].lower().startswith("revert")
        out.append(
            {
                "schema_version": "1.0",
                "event_type": "pr",
                "repo": repo,
                "pr_number": p["number"],
                "commit_sha": sha,
                "status": "merged",
                "occurred_at": p["mergedAt"],
                "first_commit_at": first,
                "lines_added": p.get("additions", 0),
                "lines_deleted": p.get("deletions", 0),
            }
        )
        out.append(
            {
                "schema_version": "1.0",
                "event_type": "deployment",
                "repo": repo,
                "service": repo.split("/")[-1],
                "environment": "production",
                "commit_sha": sha,
                "deployed_at": p["mergedAt"],
                "status": "rollback" if is_revert else "success",
                "pipeline_url": p["url"],
                "first_commit_at": first,
                "pr_merged_at": p["mergedAt"],
            }
        )
        if is_revert:
            out.append(
                {
                    "schema_version": "1.0",
                    "event_type": "rework",
                    "repo": repo,
                    "deployment_sha": sha,
                    "rework_type": "rollback",
                    "triggered_at": p["mergedAt"],
                    "user_visible": True,
                }
            )
    return out


def fetch_prs(repo: str, now: datetime, days: int) -> list[dict]:
    """Merged PRs from the last `days`, fetched in daily slices (GraphQL node limit)."""
    seen: dict[int, dict] = {}
    for start in range(days + 1):
        day = (now - timedelta(days=start)).date()
        res = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "merged",
                "--limit",
                "40",
                "--search",
                f"merged:{day}",
                "--json",
                FIELDS,
            ],
            capture_output=True,
            check=False,
            text=True,
        )
        if res.returncode:
            raise SystemExit(f"gh failed for {repo}: {res.stderr.strip()}")
        batch = json.loads(res.stdout)
        if len(batch) == 40:
            print(
                f"warning: {repo} {day} hit the 40-PR cap; some PRs missed",
                file=sys.stderr,
            )
        for p in batch:
            seen[p["number"]] = p
    return list(seen.values())


def post(url: str, events: list[dict]) -> None:
    headers = {"Content-Type": "application/json"}
    if key := os.environ.get("DORA_API_KEY"):
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        f"{url}/event/batch", json.dumps(events).encode(), headers
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"posted {len(events)} events: HTTP {resp.status}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("repos", nargs="+", help="owner/name")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--post", metavar="URL", help="dora-api base URL; omit for dry-run")
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    for repo in args.repos:
        events = events_for(repo, fetch_prs(repo, now, args.days), now, args.days)
        if args.post:
            if events:
                post(args.post, events)
            else:
                print(f"{repo}: no merged PRs in last {args.days}d", file=sys.stderr)
        else:
            for e in events:
                print(json.dumps(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
