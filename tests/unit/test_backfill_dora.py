from __future__ import annotations

"""Backfill script turns merged-PR history into schema-valid DORA events."""

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "backfill", ROOT / "scripts" / "backfill_dora_from_github.py"
)
backfill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backfill)

NOW = datetime(2026, 10, 17, tzinfo=timezone.utc)


def pr(number, title, merged, sha="a" * 40, first="2026-10-10T08:00:00Z"):
    return {
        "number": number,
        "title": title,
        "url": f"https://github.com/paruff/x/pull/{number}",
        "mergedAt": merged,
        "mergeCommit": {"oid": sha},
        "additions": 5,
        "deletions": 2,
        "commits": [{"authoredDate": first}],
    }


def validate(event):
    schema = json.loads(
        (ROOT / "dora/events" / f"{event['event_type']}-event.schema.json").read_text()
    )
    jsonschema.Draft7Validator(schema).validate(event)


def test_merged_pr_yields_valid_deployment_and_pr_events():
    events = backfill.events_for(
        "paruff/x", [pr(1, "feat: a", "2026-10-12T10:00:00Z")], NOW, 30
    )
    assert [e["event_type"] for e in events] == ["pr", "deployment"]
    for e in events:
        validate(e)
    deploy = events[1]
    assert deploy["status"] == "success"
    assert deploy["first_commit_at"] == "2026-10-10T08:00:00Z"
    assert deploy["pr_merged_at"] == "2026-10-12T10:00:00Z"


def test_revert_pr_is_rollback_with_user_visible_rework():
    events = backfill.events_for(
        "paruff/x", [pr(2, 'Revert "feat: a"', "2026-10-13T10:00:00Z")], NOW, 30
    )
    types = {e["event_type"]: e for e in events}
    assert types["deployment"]["status"] == "rollback"
    assert types["rework"]["rework_type"] == "rollback"
    assert types["rework"]["user_visible"] is True
    assert types["rework"]["deployment_sha"] == types["deployment"]["commit_sha"]
    for e in events:
        validate(e)


def test_prs_outside_window_or_unmerged_are_skipped():
    old = pr(3, "feat: old", "2026-08-01T10:00:00Z")
    unmerged = pr(4, "feat: wip", None)
    assert backfill.events_for("paruff/x", [old, unmerged], NOW, 30) == []


def test_events_are_ordered_oldest_first():
    prs = [
        pr(6, "feat: b", "2026-10-15T10:00:00Z"),
        pr(5, "feat: a", "2026-10-11T10:00:00Z"),
    ]
    deploys = [
        e
        for e in backfill.events_for("paruff/x", prs, NOW, 30)
        if e["event_type"] == "deployment"
    ]
    assert [d["deployed_at"] for d in deploys] == sorted(
        d["deployed_at"] for d in deploys
    )
