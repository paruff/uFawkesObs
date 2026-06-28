# M4-02 Ecosystem Context Review

**Date:** 2026-06-28
**Reviewer:** Agent session (M3-03 implementation)
**Scope:** M4-02 (DevLake integration) assessed against the new plane ecosystem

---

## Ecosystem Discovery

Two new planes now exist that impact M4-02's scope:

| Plane | Repo | What It Provides | Impact on M4-02 |
|---|---|---|---|
| **uFawkesRes** | [paruff/uFawkesRes](https://github.com/paruff/uFawkesRes) | Shared Postgres, Valkey, Traefik, Authelia on `fawkes-backbone-net` | DevLake could use shared Postgres instead of MySQL |
| **uFawkesDORA** | [paruff/ufawkesdora](https://github.com/paruff/ufawkesdora) | DORA metrics ingestion API, compute engine, collectors, PostgreSQL/TimescaleDB | DevLake overlaps with uFawkesDORA's native ingestion pipeline |

---

## Finding 1: DevLake Belongs in uFawkesDORA, Not uFawkesObs

The original M4-02 issue (#81) was written before uFawkesDORA existed as a separate repo. Now that the DORA plane has its own:

- `docker-compose.integration.yml`
- PostgreSQL/TimescaleDB database (for event storage)
- Ingestion API + async worker + compute engine
- GitHub Actions collectors and webhook receivers

**DevLake (Apache DevLake)** and **uFawkesDORA** serve overlapping purposes — both collect delivery events and make them queryable. Adding DevLake to uFawkesObs would create a split-brain DORA pipeline where events go to both DevLake (MySQL in uFawkesObs) and uFawkesDORA (Postgres in its own stack). This duplicates effort without clear benefit.

**Recommendation:** Move DevLake into uFawkesDORA's stack (or replace with uFawkesDORA's native ingestion). Remove DevLake from uFawkesObs's scope.

## Finding 2: uFawkesRes Changes the Database Equation

M4-02 spec says MySQL. But:
- uFawkesRes provides shared PostgreSQL 16 Alpine on `fawkes-backbone-net`
- uFawkesDORA already uses PostgreSQL + TimescaleDB
- DevLake [supports PostgreSQL since v1.0](https://devlake.apache.org/docs/Overview/SupportedDataSources)

If DevLake moves to uFawkesDORA, it could share the same PostgreSQL (or use a separate `devlake` schema). If it stays in uFawkesObs, it should connect to uFawkesRes's Postgres instead of running its own MySQL.

**Recommendation:** If DevLake is kept, switch from MySQL to PostgreSQL and connect via `fawkes-backbone-net`.

## Finding 3: Grafana Datasource Ownership Is Unclear

M4-02 says to add a DevLake datasource to uFawkesObs's `config/grafana/provisioning/datasources/datasources.yaml`. But:
- uFawkesDORA needs its own datasource (Postgres/TimescaleDB) in Grafana too
- If DevLake moves to uFawkesDORA, the datasource provisioning belongs there
- uFawkesObs should remain the Grafana host, but datasource config could be pushed from uFawkesDORA

**Recommendation:** Clarify datasource ownership. Either:
- (a) uFawkesObs provisions all datasources, uFawkesDORA provides the config via an integration guide
- (b) uFawkesDORA pushes datasource config to Grafana's provisioning API at startup

## Finding 4: DORA Recording Rules (M4-03) and Dashboard (M4-04) Still Belong in uFawkesObs

The Prometheus recording rules and Grafana dashboard for DORA are still uFawkesObs's responsibility because:
- Prometheus lives in uFawkesObs
- Grafana lives in uFawkesObs
- Recording rules query Prometheus metrics (scraped by uFawkesObs from OTel Collector)

These don't move.

---

## Updated Recommendations

| Original M4 Task | Updated Scope | Reason |
|---|---|---|
| M4-01: DORA data contract | ✅ Keep in uFawkesObs | Defines what deployment/incident means for all planes |
| **M4-02: DevLake + MySQL** | **❌ Move to uFawkesDORA** | uFawkesDORA is the DORA metrics plane; DevLake overlaps with its native ingestion |
| M4-03: DORA recording rules | ✅ Keep in uFawkesObs | Prometheus lives here |
| M4-04: DORA Grafana dashboard | ✅ Keep in uFawkesObs | Grafana lives here (data from Prometheus + Postgres) |

**Action item:** Reopen/re-title issue #81 to reflect DevLake moving to uFawkesDORA, and create a mirror issue in paruff/ufawkesdora to handle the actual DevLake integration.

---

## Cross-Plane Dependency Graph (Updated)

```
uFawkesRes ──┬──> uFawkesObs (sends telemetry)
             ├──> uFawkesPipe (sends telemetry)
             ├──> uFawkesDORA (sends telemetry, uses Postgres)
             └──> uFawkesDevX (sends telemetry)

uFawkesObs ──> Grafana (used by all planes for visualization)

uFawkesDORA ──> uFawkesRes (uses shared Postgres via fawkes-backbone-net)
              ──> uFawkesObs (uses Grafana for dashboards, Prometheus for metrics)

uFawkesPipe ──> uFawkesObs (sends deployment events as OTLP traces)
uFawkesDevX ──> uFawkesObs (sends dev telemetry as OTLP traces/metrics/logs)
```
