# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for uFawkesObs.

ADRs document deliberate technology decisions — choices that were made intentionally and
for specific reasons. Undocumented decisions look like ignorance; documented decisions
look like engineering judgment.

Each ADR follows the format:
**Context → Decision → Rationale → Consequences**

---

## Index

| ADR                                        | Title                                                                       | Status   | Date       |
| ------------------------------------------ | --------------------------------------------------------------------------- | -------- | ---------- |
| [ADR-001](ADR-001-loki-version.md)         | Use Loki 2.9.10 for Log Aggregation                                         | Accepted | 2025-06-01 |
| [ADR-002](ADR-002-docker-compose-scope.md) | Docker Compose as the Primary Deployment Runtime                            | Accepted | 2025-06-01 |
| [ADR-003](ADR-003-gitops-scope.md)         | GitOps at the Configuration Layer; Push-Triggered Deployment Reconciliation | Accepted | 2025-06-01 |

---

## Quick Reference

**Why Loki 2.9.10 and not 3.x?**
→ [ADR-001](ADR-001-loki-version.md): Loki 3.x introduces breaking schema migration risk;
2.9.x is stable and production-proven. Upgrade planned for v0.2.0.

**Why Docker Compose and not Kubernetes?**
→ [ADR-002](ADR-002-docker-compose-scope.md): Target audience is small teams on single VMs.
Docker Compose is the lowest-friction path. Kubernetes (Helm) track planned for M5.

**Why is GitOps "push-triggered" and not pull-based?**
→ [ADR-003](ADR-003-gitops-scope.md): Docker Compose has no controller loop. Pull-based
reconciliation requires Helm + ArgoCD (M5 track). GitOps here means all config in Git,
declarative, no UI-driven changes.

---

## ADR Status Definitions

| Status         | Meaning                                                       |
| -------------- | ------------------------------------------------------------- |
| **Proposed**   | Under discussion; not yet implemented                         |
| **Accepted**   | Approved and implemented                                      |
| **Deprecated** | Superseded but preserved for history                          |
| **Superseded** | Replaced by a later ADR (link provided in the superseded ADR) |

---

## Adding a New ADR

1. Copy an existing ADR as a template.
2. Number sequentially: `ADR-004-short-title.md`.
3. Add a row to the index table above.
4. Reference this README in your PR description.
