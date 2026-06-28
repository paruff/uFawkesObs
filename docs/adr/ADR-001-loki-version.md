# ADR-001: Use Loki 3.3.2 for Log Aggregation

**Status:** Accepted (updated 2026-06-28)
**Date:** 2025-06-01 (original), 2026-06-28 (updated)
**Deciders:** uFawkesObs maintainers
**Issue:** [M1-02](https://github.com/paruff/uFawkesObs/issues/68)

---

## Context

Loki 3.x reached general availability with significant architectural changes: a new storage
engine (TSDB-based index), a revised schema (schema v13), and new compactor behaviour.
Migrating from Loki 2.x to Loki 3.x requires an explicit, manual schema migration step
and carries a risk of data loss if executed incorrectly.

uFawkesObs targets small teams running single-VM workloads. The initial release (v0.1.0)
pinned Loki to 2.9.10 to avoid migration risk before the tooling matured.

### Original Decision (2025-06-01)

The original ADR (accepted 2025-06-01) decided to **pin Loki to version 2.9.10** for the
v0.1.0 release. The rationale was:

1. **Schema migration risk** — Loki 3.x requires migrating the index schema from v11/v12
   to v13. An incomplete migration leaves Loki unable to query historical data.
2. **Storage engine change** — Loki 3.x replaces BoltDB Shipper with TSDB as the default
   index store.
3. **Community hardening in progress** — The official migration tooling was still maturing.
4. **2.9.x was sufficient** — All required features (LogQL, structured metadata, label
   filtering) were fully supported.
5. **Target audience risk tolerance** — Small teams on single VMs cannot absorb downtime.

---

## Updated Decision (2026-06-28)

**Use Loki version 3.3.2** (`grafana/loki:3.3.2`).

The migration from 2.9.10 → 3.3.2 was completed in PR #116. The upgrade path used a
fresh-install strategy on a secondary storage volume, followed by a controlled cutover,
avoiding the in-place schema migration risk.

---

## Migration Summary

| Detail              | Value                                                    |
| ------------------- | -------------------------------------------------------- |
| **Previous version** | `grafana/loki:2.9.10`                                    |
| **Current version**  | `grafana/loki:3.3.2`                                     |
| **PR**               | [#116](https://github.com/paruff/uFawkesObs/pull/116)    |
| **Date**             | 2026-06-28                                               |
| **Strategy**         | Fresh-install with data replay; no in-place schema migration |
| **Schema**           | v13 (TSDB index) — configured in `config/loki/loki.yaml` |
| **Config changes**   | New `schema_config` with v13, TSDB shipper config, compactor tuning |

### Migration Approach

Rather than running the in-place `loki-upgrade` tool (which carried schema migration risk),
the team used a **parallel fresh-install strategy**:

1. A new Loki 3.3.2 instance was started with a fresh storage directory and v13 schema.
2. Source applications were pointed to the new instance (no data migration was needed
   for the initial deployment since v0.1.0 had limited historical data).
3. The old 2.9.10 instance was decommissioned.

This avoided the risk of an in-place schema migration failure while providing the benefits
of Loki 3.x going forward.

### Key Configuration Changes

- `schema_config` updated from v11 (BoltDB) to v13 (TSDB)
- `storage_config` updated from BoltDB shipper to TSDB shipper
- Compactor configuration added for TSDB index store
- Retention policy validated against v13 schema behaviour

---

## Rationale for Upgrade

1. **Migration risk was acceptable with fresh-install strategy** — Using a fresh instance
   with no in-place migration eliminated the primary risk that motivated the original pin.

2. **TSDB index performance** — Loki 3.x's TSDB index provides significantly better query
   performance for high-cardinality label sets, which is the expected usage pattern in a
   multi-service observability stack.

3. **OTLP log ingestion improvements** — Loki 3.3.2 provides native OpenTelemetry log
   ingestion improvements over 2.9.x, aligning with uFawkesObs's OTel-first architecture.

4. **Community hardening complete** — The migration tooling and documentation have matured
   since the original ADR. Fresh-install workflows are well-documented.

5. **v13 is the current stable schema** — Grafana Labs recommends v13 for all new
   deployments. Continuing on v11 would accumulate technical debt.

---

## Consequences

### Positive

- TSDB index provides better query performance for high-cardinality label sets.
- Native OTLP log ingestion improvements align with OTel-first architecture.
- v13 schema is the current stable schema; no further migration required.
- No data was lost in the migration (fresh-install strategy on a deployment with
  limited historical data).

### Negative / Trade-offs

- The fresh-install approach required re-pointing source applications; this was
  acceptable for the v0.1.0 deployment but would be more involved for a production
  deployment with significant historical data.
- Teams running uFawkesObs with a meaningful Loki data store should plan a proper
  migration path if they are still on 2.9.x.

### For Agents

- **Do not change the Loki version in `compose.yaml` without updating this ADR.**
- The Loki config file is `config/loki/loki.yaml` — schema v13, TSDB shipper.
- Prometheus scrape targets for Loki should use `http://loki:3100`.
- Alloy pushes logs to Loki at `http://loki:3100/loki/api/v1/push`.

---

## Superseded Original Decision

The original decision (pin to Loki 2.9.10) was correct for the v0.1.0 release. The
conditions that justified it (migration tooling immaturity, concern about in-place schema
migration risk) were valid at the time. Once the team demonstrated a safe migration path
(fresh-install strategy with data replay), the upgrade became the correct choice.

The original ADR text is preserved in the Git history of this file.

---

## Upgrade Path Reference

- Official migration guide: <https://grafana.com/docs/loki/latest/setup/upgrade/>
- Schema v13 reference: <https://grafana.com/docs/loki/latest/operations/storage/schema/>
- Loki 3.x release notes: <https://grafana.com/docs/loki/latest/release-notes/>
- Migration PR: [#116](https://github.com/paruff/uFawkesObs/pull/116)
