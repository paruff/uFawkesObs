"""Facade for event_queue operations.

SQLite is the only backend (self-contained ``dora`` profile). main.py and
worker.py import from here rather than from queue_sqlite.py directly.
"""

from ingestion.api.queue_sqlite import (  # noqa: F401
    close_pool,
    dequeue_next,
    enqueue_event,
    enqueue_events,
    get_pool,
    get_queue_depth,
    mark_done,
    mark_failed,
    write_raw_event,
)
