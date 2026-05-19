# ADR-001: Use Loki 2.9.10 for Log Aggregation

**Status:** Accepted  
**Date:** 2025-06-01  
**Deciders:** uFawkesObs maintainers  
**Issue:** [M1-02](https://github.com/paruff/uFawkesObs/issues/)

---

## Context

Loki 3.x reached general availability with significant architectural changes: a new storage
engine (TSDB-based index), a revised schema (schema v13), and new compactor behaviour.
Migrating from Loki 2.x to Loki 3.x requires an explicit, manual schema migration step
and carries a risk of data loss if executed incorrectly. Community hardening of the official
migration tooling (`loki-upgrade`) was still in progress at the time of the first uFawkesObs
release.

uFawkesObs targets small teams running single-VM workloads. For this audience, an
in-place upgrade failure with no HA failover path is a critical risk. Stability and
operational simplicity outweigh access to new features at the v0.1 stage.

---

## Decision

**Pin Loki to version 2.9.10** (`grafana/loki:2.9.10`) for the initial release.

Loki 2.9.x is the final long-term-supported release of the 2.x line. It is stable,
production-proven, and fully compatible with the Grafana 10.x datasource plugin included
in this stack.

---

## Rationale

1. **Schema migration risk** — Loki 3.x requires migrating the index schema from v11/v12
   to v13. An incomplete migration leaves Loki unable to query historical data. There is no
   rollback path without a full data restore.

2. **Storage engine change** — Loki 3.x replaces BoltDB Shipper with TSDB as the default
   index store. Existing deployments using the `filesystem` storage (as configured in this
   stack) require non-trivial compactor and schema configuration changes.

3. **Community hardening in progress** — At the time of this decision, the official Loki
   upgrade guide for 2.x → 3.x had open issues tracking edge cases in the migration
   tooling. The Grafana Labs community forums showed multiple reports of failed migrations
   on single-instance deployments.

4. **2.9.x is stable and sufficient** — All features required by this stack (LogQL,
   structured metadata, label-based filtering, Grafana datasource integration) are fully
   supported in 2.9.x. There is no functional reason to migrate before the tooling matures.

5. **Target audience risk tolerance** — Small teams on single VMs cannot absorb observability
   downtime. Stability is the primary constraint.

---

## Consequences

### Positive

- No schema migration required for initial deployment.
- Fully compatible with all existing LogQL queries and Grafana datasource configuration.
- Lower operational risk for the target audience.

### Negative / Trade-offs

- Loki 2.9.x will eventually reach end-of-life. Adopters should not build long-term
  dependency on 2.9.x-only features.
- Some Loki 3.x features (OTLP log ingestion improvements, native OpenTelemetry support
  enhancements) are not available.

### Planned Resolution

- Upgrade to Loki 3.x is planned for **v0.2.0**, once:
  1. The migration tooling is declared stable by Grafana Labs.
  2. The schema migration path for `filesystem`-backed single-instance deployments is
     documented with a tested rollback procedure.
  3. uFawkesObs has added a pre-upgrade data backup script.

---

## Upgrade Path Reference

When upgrading from Loki 2.9.x to 3.x:

- Official migration guide: <https://grafana.com/docs/loki/latest/setup/upgrade/>
- Schema migration specifics: <https://grafana.com/docs/loki/latest/operations/storage/schema/>
- Breaking changes list: <https://grafana.com/docs/loki/latest/release-notes/>

Adopters should read the Loki release notes for every minor version between 2.9.10 and
the target 3.x version before upgrading.

---

## Superseded By

This ADR will be superseded by **ADR-004** (planned) when the Loki 3.x upgrade is
implemented in v0.2.0.
