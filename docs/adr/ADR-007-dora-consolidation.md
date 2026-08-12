# ADR-007: Merge uFawkesDORA Compute Plane into uFawkesObs

**Status:** Accepted
**Date:** 2026-08-12
**Companion issues:** #201–#208 (DORA-CONSOLIDATION-01 through 08, created 2026-08-12)
**Scope:** Moves all uFawkesDORA code, configs, dashboards, alerts, tests, and docs
into uFawkesObs; archives the standalone uFawkesDORA repo.

---

## Context

| Key Question | Answer |
|-------------|--------|
| **Why now?** | uFawkesObs already defines the `dora-api` service and `dora` Compose profile, but the Python ingestion/compute code and database init scripts never moved. The standalone uFawkesDORA repo adds operational friction (cross-repo CI, duplicate toolchain configs, stale `opencode.yaml`) without delivering architectural separation — its compute plane is stateless and naturally belongs inside the observability plane that already owns the OTel pipeline, Prometheus rules, and Grafana dashboards for DORA. |
| **What moves?** | `ingestion/`, `compute/`, `events/`, `database/init/`, 5 additional Grafana dashboards, 2 alert-rule files, collector patterns, and the DORA test suite (5 tests). uFawkesObs's existing DORA recording rules, dashboard, and ADR-006 data contract remain — the new code extends them. |
| **What does not move?** | The standalone `docker-compose.dev.yml` (replaced by uFawkesObs's `dora` profile), the standalone CI workflows (replaced by uFawkesObs's existing CI), and the `docs/plan/plan.md` (its architecture section is superseded by this ADR). |
| **What happens to the uFawkesDORA repo?** | Archived with a README pointing to uFawkesObs as the successor. GitHub metadata updated to mark it read-only. |

## Decision

### Architecture After Consolidation

```
┌─────────────────────────────────────────────────────────────┐
│  uFawkesObs — Observability + DORA Compute Plane            │
│                                                             │
│  dora/                       ← new top-level directory      │
│  ├── ingestion/              ← FastAPI event ingestion      │
│  ├── compute/                ← DORA metrics Compute engine   │
│  ├── events/                 ← JSON schemas                 │
│  ├── database/init/          ← PostgreSQL/TimescaleDB init  │
│  └── collectors/             ← CI/CD collector patterns     │
│                                                             │
│  dashboards/platform/        ← Grafana dashboards (merged)  │
│  config/prometheus/rules/   ← alert rules (merged)          │
│  tests/unit/test_dora*.py    ← DORA test suite (new)        │
│                                                             │
│  compose.yaml (expanded):                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ dora-api      (existing — fixed volume mount)       │    │
│  │ dora-compute  (new — queue worker + metrics compute)│    │
│  │ postgres      (existing — shared PG, dora profile)  │    │
│  │ otel-collector-dora (existing — unchanged)          │    │
│  │ ufawkesres-postgres (existing — full profile)       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Target State by Artifact

| Artifact | Current Location | Target Location in uFawkesObs |
|----------|-----------------|-------------------------------|
| Ingestion API | `ufawkesdora/ingestion/` | `dora/ingestion/` |
| Compute engine | `ufawkesdora/compute/` | `dora/compute/` |
| Event schemas | `ufawkesdora/events/` | `dora/events/` |
| DB init scripts | `ufawkesdora/database/init/` | `dora/database/init/` |
| TimescaleDB hypertables | `ufawkesdora/database/timescaledb/` | `dora/database/timescaledb/` |
| DB migrations | `ufawkesdora/database/migrations/` | `dora/database/migrations/` |
| Grafana dashboards (8) | `ufawkesdora/dashboards/` | `dashboards/platform/` (merge with existing `dora-metrics.json`) |
| Alert rules (2) | `ufawkesdora/alerts/` | `config/prometheus/rules/` (rename with `ufawkesobs-` prefix) |
| Collector patterns | `ufawkesdora/collectors/` | `dora/collectors/` |
| Integration tests | `ufawkesdora/tests/` | `tests/` (merge into unit/integration/e2e) |
| DORA spec | `ufawkesdora/docs/spec/` | `docs/dora/specification.md` |
| DORA design | `ufawkesdora/docs/design/` | `docs/dora/design.md` |
| Pipeline decisions | `ufawkesdora/docs/decisions/` | `docs/dora/decisions/` |

### Compose Changes

1. **Fix `dora-api` volume mount**: Change `./ingestion:/app/ingestion:ro` → `./dora/ingestion:/app/ingestion:ro`.
2. **Add `dora-compute` service** (new, `dora` + `full` profiles): Long-running
   compute loop + queue worker, volume mount `./dora/compute:/app/compute:ro`,
   same `DATABASE_URL` env as dora-api.
3. **Restructure `postgres` init volume**: Change to mount
   `./dora/database/init/` and `./dora/database/timescaledb/hypertables.sql`.
4. **No change** to `otel-collector-dora` or `ufawkesres-postgres`.

### `pyproject.toml`

Add entry points for the new services:

```toml
[project.scripts]
ufawkesdora-ingestion = "dora.ingestion.api:main"
ufawkesdora-compute = "dora.compute.compute_engine:main"
ufawkesdora-queue = "dora.compute.queue_worker:main"
```

Merge `ufawkesdora` dependencies (`psycopg[binary]`, `fastapi`, `uvicorn`,
`pydantic`, `structlog`, `httpx`, `asyncpg`, `python-json-logger`) into
existing `pyproject.toml`.

### Archive uFawkesDORA

- Add deprecation notice to `README.md` pointing to uFawkesObs.
- Set repo description to `[ARCHIVED — merged into uFawkesObs]`.
- Enable GitHub archive (read-only, issues closed).
- Leave the git history intact.

## Consequences

- **Positive:** Single repo to maintain, one CI pipeline, one set of toolchain
  configs, no cross-repo PR coordination for DORA changes. The `dora` Compose
  profile becomes self-contained.
- **Negative:** Larger repo size (~1,700 lines of Python + dashboards/JSON +
  SQL). No architectural penalty — the compute plane was already stateless and
  depended on uFawkesObs's OTel pipeline.
- **Risk:** Low. The existing `dora-api` service in `compose.yaml` already
  defines the contracts; we are just landing the code that fulfills them.
