"""SQLite-backed event_queue operations (aiosqlite).

Default backend for the ``dora`` profile — self-contained, zero external
dependencies. Selected via queue.py when DATABASE_URL is unset or points at
SQLite. Runs as a single shared connection since the worker loop executes
in-process inside dora-api (see main.py's lifespan), so there is no
multi-writer contention to guard against with row locking. See
queue_postgres.py for the resource-plane / suite-mode backend.
"""

import json
import os
from contextlib import asynccontextmanager

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS event_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT    NOT NULL,
    source          TEXT    NOT NULL,
    payload         TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending',
    attempts        INTEGER NOT NULL DEFAULT 0,
    received_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at    TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_queue_status_received
    ON event_queue (status, received_at);

CREATE TABLE IF NOT EXISTS raw_events (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    event_queue_id      INTEGER REFERENCES event_queue(id),
    event_type          TEXT    NOT NULL,
    source              TEXT    NOT NULL,
    outcome             TEXT    NOT NULL,
    duration_seconds    INTEGER,
    metadata            TEXT,
    recorded_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ── Connection ───────────────────────────────────────────────────────────────

_pool: aiosqlite.Connection | None = None


def _sqlite_path(dsn: str) -> str:
    """Translate a sqlite:// DSN into a path aiosqlite understands.

    sqlite://:memory:      -> :memory:
    sqlite:///relative.db  -> relative.db
    sqlite:////absolute.db -> /absolute.db
    """
    if dsn in ("sqlite://:memory:", ":memory:"):
        return ":memory:"
    if dsn.startswith("sqlite:////"):
        return dsn[len("sqlite:///") :]
    if dsn.startswith("sqlite:///"):
        return dsn[len("sqlite:///") :]
    if dsn.startswith("sqlite://"):
        return dsn[len("sqlite://") :]
    return dsn


async def get_pool(
    dsn: str | None = None, min_size: int = 2, max_size: int = 10
) -> aiosqlite.Connection:
    """Get or create the shared aiosqlite connection.

    If ``dsn`` is ``None``, uses the ``DATABASE_URL`` environment variable.
    ``min_size``/``max_size`` are accepted for interface parity with
    queue_postgres.get_pool() but unused — SQLite here is single-connection.
    """
    global _pool
    if _pool is None:
        if dsn is None:
            dsn = os.environ["DATABASE_URL"]
        _pool = await aiosqlite.connect(_sqlite_path(dsn))
        await _pool.executescript(_SCHEMA)
        await _pool.commit()
    return _pool


async def close_pool():
    """Close the shared connection."""
    global _pool
    if _pool is not None:
        await _pool.close()
    _pool = None


@asynccontextmanager
async def _connect():
    """Yield the shared connection, committing on a clean exit."""
    conn = await get_pool()
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise


# ── Queue operations ────────────────────────────────────────────────────────


async def enqueue_event(payload: dict) -> int:
    """Insert an event into the event_queue and return its id."""
    event_type: str = payload.get("event_type", "unknown")
    source: str = payload.get("repo", "unknown")

    async with _connect() as conn:
        cursor = await conn.execute(
            "INSERT INTO event_queue (event_type, source, payload) VALUES (?, ?, ?)",
            (event_type, source, json.dumps(payload)),
        )
        return cursor.lastrowid


async def enqueue_events(payloads: list[dict]) -> list[int]:
    """Insert multiple events. SQLite has no cross-statement RETURNING, so
    ids are read back from lastrowid, which is safe here since writes are
    serialized through the single shared connection."""
    ids: list[int] = []
    async with _connect() as conn:
        for payload in payloads:
            event_type: str = payload.get("event_type", "unknown")
            source: str = payload.get("repo", "unknown")
            cursor = await conn.execute(
                "INSERT INTO event_queue (event_type, source, payload) "
                "VALUES (?, ?, ?)",
                (event_type, source, json.dumps(payload)),
            )
            ids.append(cursor.lastrowid)
    return ids


async def get_queue_depth() -> int:
    """Return the number of pending (not yet processed) events."""
    async with _connect() as conn:
        row = await (
            await conn.execute(
                "SELECT COUNT(*) FROM event_queue WHERE status = 'pending'"
            )
        ).fetchone()
        return row[0]


# ── Worker operations ───────────────────────────────────────────────────────


async def dequeue_next() -> dict | None:
    """Claim the next pending event.

    No SKIP LOCKED needed: the worker loop runs in-process inside dora-api
    against this single shared connection, so there is only ever one reader.
    """
    async with _connect() as conn:
        row = await (
            await conn.execute(
                """
                UPDATE event_queue
                SET status = 'processing'
                WHERE id = (
                    SELECT id
                    FROM event_queue
                    WHERE status = 'pending'
                    ORDER BY received_at
                    LIMIT 1
                )
                RETURNING id, payload, event_type, source, attempts
                """
            )
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "payload": json.loads(row[1]),
            "event_type": row[2],
            "source": row[3],
            "attempts": row[4],
        }


async def mark_done(event_id: int):
    """Mark an event as successfully processed."""
    async with _connect() as conn:
        await conn.execute(
            "UPDATE event_queue "
            "SET status = 'done', processed_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            (event_id,),
        )


async def mark_failed(event_id: int, max_attempts: int = 3):
    """Increment attempts and mark as 'error' if max_attempts reached.

    If the event still has attempts remaining, it is set back to 'pending'
    so another worker can retry it.
    """
    async with _connect() as conn:
        await conn.execute(
            """
            UPDATE event_queue
            SET attempts = attempts + 1,
                status = CASE
                    WHEN attempts + 1 >= ? THEN 'error'
                    ELSE 'pending'
                END,
                processed_at = CASE
                    WHEN attempts + 1 >= ? THEN CURRENT_TIMESTAMP
                    ELSE processed_at
                END
            WHERE id = ?
            """,
            (max_attempts, max_attempts, event_id),
        )


async def write_raw_event(
    event_queue_id: int,
    event_type: str,
    source: str,
    outcome: str,
    payload: dict,
    duration_seconds: int | None = None,
):
    """Write a processed event to the raw_events table."""
    async with _connect() as conn:
        await conn.execute(
            """
            INSERT INTO raw_events
                (event_queue_id, event_type, source, outcome,
                 duration_seconds, metadata, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                event_queue_id,
                event_type,
                source,
                outcome,
                duration_seconds,
                json.dumps(payload),
            ),
        )
