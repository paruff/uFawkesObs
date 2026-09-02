"""uFawkesDORA Ingestion API — stateless FastAPI ingestion endpoint.

Accepts events on ``POST /event``, validates against canonical schemas,
and enqueues to Postgres using the event_queue table.

Endpoints:
    POST /event       — Accept a single event, validate, enqueue.
    POST /event/batch — Accept multiple events, validate all, enqueue in a transaction.
    GET  /health      — Health check with queue depth.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from compute.metrics import compute_all_metrics, render_prometheus_text
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from ingestion.api.auth import require_api_key
from ingestion.api.queue import (
    close_pool,
    enqueue_event,
    enqueue_events,
    get_queue_depth,
)
from ingestion.api.validator import validate_payload, validate_payloads
from ingestion.processor.worker import run_worker_loop

logger = logging.getLogger(__name__)

COMPUTE_INTERVAL_SECONDS = int(os.getenv("DORA_COMPUTE_INTERVAL_SECONDS", "3600"))
COMPUTE_WINDOW_DAYS = int(os.getenv("DORA_COMPUTE_WINDOW_DAYS", "30"))

# Latest rendered exposition text, refreshed by the compute loop and served by
# GET /metrics. Empty until the first cycle completes, so a scrape arriving
# during startup gets an empty (still valid) response rather than a 500.
_metrics_text: str = ""


async def run_compute_loop(shutdown_event: asyncio.Event) -> None:
    """Recompute DORA metrics on an interval and cache them for /metrics.

    Runs in-process rather than as a separate dora-compute container, for the
    same reason the event_queue worker does (issue #205), plus one specific to
    this loop: dora-compute wrote dora_snapshots to the same SQLite file the
    API writes events to, from a second process. The database runs in
    rollback-journal mode (journal_mode=delete), where a writer takes an
    exclusive lock that blocks readers too — so the split guaranteed
    cross-process contention for no isolation benefit on a single-node stack.

    Each cycle is guarded: a failure logs with traceback and waits for the next
    interval rather than killing the task, so one transient DB error cannot
    silently stop metric refresh for the life of the container.
    """
    global _metrics_text
    while not shutdown_event.is_set():
        try:
            results = await compute_all_metrics(window_days=COMPUTE_WINDOW_DAYS)
            _metrics_text = render_prometheus_text(results)
            logger.info("DORA metrics refreshed for %d team(s)", len(results))
        except Exception:
            # Logged with traceback, never swallowed: a metrics pipeline that
            # stops updating must be visible, not inferred from stale graphs.
            logger.exception("DORA compute cycle failed; retrying next interval")
        try:
            await asyncio.wait_for(
                shutdown_event.wait(), timeout=COMPUTE_INTERVAL_SECONDS
            )
        except TimeoutError:
            continue


# ── Lifecycle ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle.

    Runs the event_queue worker loop and the DORA compute loop as background
    tasks rather than separate containers (issue #205) — the connection pool is
    shared and lazy-initialized on first use by the API or either loop.
    """
    shutdown_event = asyncio.Event()
    worker_task = asyncio.create_task(run_worker_loop(shutdown_event=shutdown_event))
    compute_task = asyncio.create_task(run_compute_loop(shutdown_event))
    yield
    # Shutdown: signal both loops to stop, then close the pool
    shutdown_event.set()
    for task in (worker_task, compute_task):
        try:
            await asyncio.wait_for(task, timeout=5)
        except (TimeoutError, asyncio.CancelledError):
            task.cancel()
    await close_pool()


app = FastAPI(
    title="uFawkesDORA Ingestion API",
    version="0.1.0",
    lifespan=lifespan,
)


# ── Exception handlers ─────────────────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    """Ensure 422 errors carry structured field-level detail."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    """Prometheus scrape endpoint for computed DORA metrics.

    Deliberately unauthenticated, matching every other /metrics in this stack
    (Prometheus scrapes them all without credentials) and bound to localhost
    by compose. It exposes aggregate delivery metrics, not event payloads.

    Served from the compute loop's cached render rather than computed per
    scrape, so scrape latency does not depend on database work and a scrape
    storm cannot amplify into database load.
    """
    return _metrics_text


@app.get("/health")
async def health():
    """Health check endpoint.

    Returns ``{"status": "ok", "queue_depth": N}`` where N is the number
    of pending events in the queue.
    """
    depth = await get_queue_depth()
    return {"status": "ok", "queue_depth": depth}


@app.post("/event", status_code=201, dependencies=[Depends(require_api_key)])
async def post_event(payload: dict[str, Any]):
    """Accept a single event, validate, and enqueue.

    Returns ``{"queued": true, "id": N}`` on success.
    Returns ``422`` with field-level errors on validation failure.
    """
    result = validate_payload(payload)
    if not result.valid:
        raise HTTPException(
            status_code=422, detail=result.to_error_response()["detail"]
        )

    event_id = await enqueue_event(payload)
    return {"queued": True, "id": event_id}


@app.post("/event/batch", status_code=201, dependencies=[Depends(require_api_key)])
async def post_events(payloads: list[dict[str, Any]]):
    """Accept multiple events, validate all, enqueue in one transaction.

    Returns ``{"queued": true, "ids": [N, ...]}`` on success.
    If *any* event fails validation, none are enqueued and a ``422`` with
    per-event field-level errors is returned.
    """
    results = validate_payloads(payloads)

    # Collect all validation errors grouped by index
    errors_by_index: dict[int, list] = {}
    all_valid = True
    for i, result in enumerate(results):
        if not result.valid:
            all_valid = False
            errors_by_index[i] = result.to_error_response()["detail"]

    if not all_valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "One or more events failed validation. None were enqueued.",
                "errors": errors_by_index,
            },
        )

    ids = await enqueue_events(payloads)
    return {"queued": True, "ids": ids}
