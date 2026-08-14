# ============================================================================
# uFawkesDORA Compute — Multi-stage Dockerfile
# ----------------------------------------------------------------------------
# Stage 1: Build / install dependencies
# Stage 2: Runtime image (non-root user, heartbeat-file health check)
#
# Build context: repository root (see compose.yaml dora-compute service).
# No pyproject.toml / console_scripts here — every dora/* service ships its
# own requirements file and a direct entrypoint (see ADR-007 amendment).
# ============================================================================

# ── Stage 1: Build ─────────────────────────────────────────────────────────────

FROM python:3.13-slim AS builder

WORKDIR /build

COPY dora/compute/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ───────────────────────────────────────────────────────────

FROM python:3.13-slim

RUN groupadd -r ufawkes && useradd -r -g ufawkes -d /app -s /sbin/nologin ufawkes

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Keeps the `compute.*` import namespace so `python -m compute.metrics` works
COPY dora/compute/__init__.py ./compute/__init__.py
COPY dora/compute/metrics.py ./compute/metrics.py
COPY dora/compute/archetype.py ./compute/archetype.py
COPY dora/compute/vsi.py ./compute/vsi.py
COPY dora/compute/run.sh ./run.sh

RUN chown -R ufawkes:ufawkes /app

USER ufawkes

# No HTTP endpoint — run.sh writes a heartbeat file after each successful
# compute cycle; unhealthy if it goes stale for more than 2x the interval.
HEALTHCHECK --interval=5m --timeout=10s --start-period=2m --retries=3 \
    CMD python3 -c "\
import os, sys, time; \
p = '/tmp/dora-compute-heartbeat'; \
stale_after = int(os.environ.get('DORA_COMPUTE_INTERVAL_SECONDS', '3600')) * 2; \
sys.exit(0 if os.path.exists(p) and time.time() - os.path.getmtime(p) < stale_after else 1)"

CMD ["/bin/sh", "run.sh"]
