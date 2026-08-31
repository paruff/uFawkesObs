"""Unit tests for the SQLite-backed event_queue implementation.

SQLite is the only event_queue backend. Uses an in-memory SQLite database
per test — see queue_sqlite.get_pool(dsn=...).
"""

import json
import sys
import tempfile
from pathlib import Path

import aiosqlite
import pytest
import pytest_asyncio

sys.path.insert(0, str(Path(__file__).parents[2] / "dora" / "ingestion"))

from api import queue_sqlite as queue  # noqa: E402

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(autouse=True)
async def _reset_pool():
    await queue.close_pool()
    yield
    await queue.close_pool()


async def _conn():
    return await queue.get_pool(dsn="sqlite://:memory:")


async def test_enqueue_event_returns_incrementing_id():
    await _conn()
    first_id = await queue.enqueue_event({"event_type": "deployment", "repo": "a"})
    second_id = await queue.enqueue_event({"event_type": "deployment", "repo": "b"})
    assert second_id == first_id + 1


async def test_enqueue_event_is_idempotent_for_identical_payload():
    """A resent (retried) payload must not double-enqueue (production-audit
    finding: event_queue had no dedup key, so a client retry silently
    double-counted DORA metrics)."""
    await _conn()
    payload = {"event_type": "deployment", "repo": "a", "commit_sha": "x" * 40}

    first_id = await queue.enqueue_event(payload)
    second_id = await queue.enqueue_event(payload)

    assert second_id == first_id
    assert await queue.get_queue_depth() == 1


async def test_enqueue_event_distinguishes_different_payloads_with_same_repo():
    await _conn()
    first_id = await queue.enqueue_event(
        {"event_type": "deployment", "repo": "a", "commit_sha": "a" * 40}
    )
    second_id = await queue.enqueue_event(
        {"event_type": "deployment", "repo": "a", "commit_sha": "b" * 40}
    )
    assert second_id != first_id
    assert await queue.get_queue_depth() == 2


async def test_get_queue_depth_counts_only_pending():
    await _conn()
    await queue.enqueue_event({"event_type": "deployment", "repo": "a"})
    await queue.enqueue_event({"event_type": "deployment", "repo": "b"})
    assert await queue.get_queue_depth() == 2


async def test_dequeue_next_returns_none_when_empty():
    await _conn()
    assert await queue.dequeue_next() is None


async def test_dequeue_next_claims_oldest_pending_and_marks_processing():
    await _conn()
    payload = {"event_type": "deployment", "repo": "a", "status": "success"}
    event_id = await queue.enqueue_event(payload)

    event = await queue.dequeue_next()

    assert event["id"] == event_id
    assert event["payload"] == payload
    assert event["event_type"] == "deployment"
    assert event["source"] == "a"
    assert event["attempts"] == 0
    # Claimed events drop out of the pending count.
    assert await queue.get_queue_depth() == 0


async def test_mark_done_sets_status_and_processed_at():
    await _conn()
    event_id = await queue.enqueue_event({"event_type": "deployment", "repo": "a"})
    await queue.dequeue_next()

    await queue.mark_done(event_id)

    async with queue._connect() as conn:  # noqa: SLF001 - test introspection
        row = await (
            await conn.execute(
                "SELECT status, processed_at FROM event_queue WHERE id = ?",
                (event_id,),
            )
        ).fetchone()
    assert row[0] == "done"
    assert row[1] is not None


async def test_mark_failed_requeues_until_max_attempts_then_errors():
    await _conn()
    event_id = await queue.enqueue_event({"event_type": "deployment", "repo": "a"})

    await queue.mark_failed(event_id, max_attempts=2)
    async with queue._connect() as conn:  # noqa: SLF001
        row = await (
            await conn.execute(
                "SELECT status, attempts FROM event_queue WHERE id = ?", (event_id,)
            )
        ).fetchone()
    assert row == ("pending", 1)

    await queue.mark_failed(event_id, max_attempts=2)
    async with queue._connect() as conn:  # noqa: SLF001
        row = await (
            await conn.execute(
                "SELECT status, attempts FROM event_queue WHERE id = ?", (event_id,)
            )
        ).fetchone()
    assert row == ("error", 2)


async def test_write_raw_event_round_trips_metadata_json():
    await _conn()
    event_id = await queue.enqueue_event({"event_type": "deployment", "repo": "a"})
    metadata = {"deployed_at": "2026-01-01T00:00:00Z", "commit_sha": "abc123"}

    await queue.write_raw_event(
        event_queue_id=event_id,
        event_type="deployment",
        source="a",
        outcome="success",
        payload=metadata,
        duration_seconds=42,
    )

    async with queue._connect() as conn:  # noqa: SLF001
        row = await (
            await conn.execute(
                "SELECT outcome, duration_seconds, metadata FROM raw_events "
                "WHERE event_queue_id = ?",
                (event_id,),
            )
        ).fetchone()
    assert row[0] == "success"
    assert row[1] == 42
    assert json.loads(row[2]) == metadata


async def test_enqueue_events_batch_inserts_all_and_returns_ids():
    await _conn()
    ids = await queue.enqueue_events(
        [
            {"event_type": "deployment", "repo": "a"},
            {"event_type": "deployment", "repo": "b"},
        ]
    )
    assert len(ids) == 2
    assert await queue.get_queue_depth() == 2


async def test_get_pool_adds_payload_hash_to_pre_existing_database():
    """Regression guard: a database created before the idempotency fix (no
    payload_hash column) must self-heal on next connect, not break enqueue.

    Discovered live against the real dora-api SQLite file, which had been
    running for two days before this fix and had no payload_hash column —
    CREATE TABLE IF NOT EXISTS alone does not add it to an existing table.
    """
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "legacy.db"

        # Simulate the pre-fix schema: event_queue with no payload_hash column.
        legacy_conn = await aiosqlite.connect(str(db_path))
        await legacy_conn.executescript(
            """
            CREATE TABLE event_queue (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type      TEXT    NOT NULL,
                source          TEXT    NOT NULL,
                payload         TEXT    NOT NULL,
                status          TEXT    NOT NULL DEFAULT 'pending',
                attempts        INTEGER NOT NULL DEFAULT 0,
                received_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processed_at    TIMESTAMP
            );
            """
        )
        await legacy_conn.execute(
            "INSERT INTO event_queue (event_type, source, payload) "
            "VALUES ('deployment', 'a', '{}')"
        )
        await legacy_conn.commit()
        await legacy_conn.close()

        # Reconnect via the real get_pool() — this must self-heal the schema.
        await queue.get_pool(dsn=f"sqlite:///{db_path}")

        # Old row survives, untouched, with payload_hash = NULL.
        assert await queue.get_queue_depth() == 1

        # New enqueue must work against the now-healed schema.
        new_id = await queue.enqueue_event({"event_type": "deployment", "repo": "b"})
        assert new_id == 2
        assert await queue.get_queue_depth() == 2
