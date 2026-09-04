# ============================================================================
# uFawkesDORA Ingestion API — Multi-stage Dockerfile
# ----------------------------------------------------------------------------
# Stage 1: Build / install dependencies
# Stage 2: Runtime image (non-root user, health check)
#
# Build context: repository root (see compose.yaml dora-api service).
# ============================================================================

# ── Stage 1: Build ─────────────────────────────────────────────────────────────

FROM python:3.13-slim AS builder

WORKDIR /build

# Install only the dependencies needed at runtime
COPY dora/ingestion/requirements-ingestion.txt requirements-ingestion.txt
RUN pip install --no-cache-dir -r requirements-ingestion.txt

# ── Stage 2: Runtime ───────────────────────────────────────────────────────────

FROM python:3.13-slim

# Create non-root user
RUN groupadd -r ufawkes && useradd -r -g ufawkes -d /app -s /sbin/nologin ufawkes

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy application code (keeps the `ingestion.*` import namespace so the
# runtime volume mount at /app/ingestion resolves — see ADR-007)
COPY dora/ingestion/__init__.py ./ingestion/__init__.py
COPY dora/ingestion/api/ ./ingestion/api/
COPY dora/ingestion/processor/ ./ingestion/processor/
COPY dora/events/ ./events/
# The DORA compute loop runs inside this service now (issue #205 pattern,
# extended from the queue worker to metrics computation), so its module
# ships here. No extra dependencies: compute only pulled in aiohttp for the
# Pushgateway push, which is lazily imported and no longer on the runtime path.
COPY dora/compute/__init__.py ./compute/__init__.py
COPY dora/compute/metrics.py ./compute/metrics.py
COPY dora/compute/metrics_db_sqlite.py ./compute/metrics_db_sqlite.py

# Ensure non-root user owns everything
RUN chown -R ufawkes:ufawkes /app

USER ufawkes

EXPOSE 8088

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8088/health')" || exit 1

CMD ["uvicorn", "ingestion.api.main:app", "--host", "0.0.0.0", "--port", "8088"]
