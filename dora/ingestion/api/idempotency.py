"""Shared idempotency-key computation for event_queue writes.

Used by queue_sqlite.py so a retried submission hashes identically — the
whole point is that a client retry (same payload, resent after a timeout)
dedupes instead of double-counting DORA metrics.
"""

import datetime
import hashlib
import json

_DEPLOYMENT_KEY = (
    "event_type",
    "repo",
    "service",
    "environment",
    "commit_sha",
    "status",
    "deployed_at",
)


def _utc(value: str) -> str:
    """Same instant, same text: `Z` and `+00:00` must hash alike."""
    try:
        return (
            datetime.datetime.fromisoformat(value).astimezone(datetime.UTC).isoformat()
        )
    except (ValueError, TypeError):
        return value


def payload_hash(payload: dict) -> str:
    """Return a stable SHA-256 hex digest of a validated event payload.

    Uses a canonical JSON encoding (sorted keys, no whitespace) so the same
    logical payload always hashes the same way regardless of field order.
    """
    if payload.get("event_type") == "deployment":
        # Optional fields can differ between retries of one deployment (AF-02).
        payload = {k: payload.get(k) for k in _DEPLOYMENT_KEY}
        payload["deployed_at"] = _utc(payload["deployed_at"])
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
