"""Backend-selecting facade for event_queue operations.

SQLite is the default (self-contained ``dora`` profile). Set DATABASE_URL to
a postgresql:// DSN to use the resource-plan / suite-mode Postgres backend
instead. main.py and worker.py import from here so they need no changes
regardless of backend.
"""

import os

if os.environ.get("DATABASE_URL", "").startswith("postgresql"):
    from ingestion.api.queue_postgres import (  # noqa: F401
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
else:
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
