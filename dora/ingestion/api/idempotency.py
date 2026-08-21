"""Shared idempotency-key computation for event_queue writes.

Used by both queue_sqlite.py and queue_postgres.py so a retried submission
hashes identically regardless of backend — the whole point is that a client
retry (same payload, resent after a timeout) dedupes instead of
double-counting DORA metrics.
"""

import hashlib
import json


def payload_hash(payload: dict) -> str:
    """Return a stable SHA-256 hex digest of a validated event payload.

    Uses a canonical JSON encoding (sorted keys, no whitespace) so the same
    logical payload always hashes the same way regardless of field order.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
