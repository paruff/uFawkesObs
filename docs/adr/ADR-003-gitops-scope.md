# ADR-003: GitOps at the Configuration Layer; Push-Triggered Deployment Reconciliation

**Status:** Accepted  
**Date:** 2025-06-01  
**Deciders:** uFawkesObs maintainers  
**Issue:** [M1-02](https://github.com/paruff/uFawkesObs/issues/68)

---

## Context

uFawkesObs describes itself as "GitOps-first." In the broader ecosystem, GitOps typically
implies a **pull-based reconciliation loop**: a controller (ArgoCD, Flux) continuously
watches a Git repository and automatically applies any detected divergence between the
desired state in Git and the actual running state of the system.

Docker Compose has no built-in controller loop. There is no Compose-native equivalent of
ArgoCD or Flux. Implementing pull-based reconciliation on top of Docker Compose requires
either a third-party controller or a custom polling daemon — both of which add significant
operational complexity that is inconsistent with the project's goal of simplicity.

The term "GitOps-first" therefore means something more specific in this context, and that
meaning must be documented to set correct expectations.

---

## Decision

**Scope GitOps to the configuration layer only.** Deployment reconciliation is
**push-triggered**, not pull-based.

"GitOps-first" in uFawkesObs means:

1. All desired state (service definitions, configuration, dashboards, alert rules) is in
   version control.
2. Configuration is declarative — no manual UI-driven changes to Grafana datasources,
   Prometheus scrape configs, or Alertmanager routes.
3. No configuration exists outside the repository that is not also reflected in the
   repository.

It does **not** mean:

- Automatic drift detection and remediation.
- Pull-based controller loops.
- Continuous reconciliation without human or CI trigger.

---

## Rationale

1. **Docker Compose has no controller loop** — Compose is an imperative orchestrator that
   applies state on demand. It does not poll for drift. Adding a controller loop to Docker
   Compose requires ArgoCD or Flux, both of which require Kubernetes. This is out of scope
   for the single-VM Docker Compose track (see ADR-002).

2. **Push-based reconciliation is sufficient for the target audience** — Small teams with
   a CI/CD pipeline (even a simple one) can trigger `docker compose up` on merge to main.
   This achieves the primary GitOps goal: config changes in Git are reflected in production.

3. **Pull-based reconciliation requires Helm + ArgoCD (M5 track)** — Full GitOps with
   automatic drift detection is the right model for Kubernetes deployments. This is
   planned for Milestone 5 alongside the Helm chart track (see ADR-002).

4. **Clarity prevents disappointment** — Teams evaluating uFawkesObs who expect
   full ArgoCD-style reconciliation will be disappointed if this is not documented. Setting
   the correct expectation up front preserves trust.

---

## What "GitOps-first" Means Here

| Practice | Supported in this release |
|---|---|
| All desired state in version control | ✅ Yes — `compose.yaml`, `config/`, `dashboards/` |
| Declarative configuration | ✅ Yes — no manual UI changes; all config is file-based |
| No out-of-band config changes | ✅ Yes — Grafana provisioning prevents UI-only changes from persisting |
| Audit trail via Git history | ✅ Yes — every config change is a commit |
| Push-triggered deployment | ✅ Yes — `make up` or CI pipeline on merge |
| Pull-based drift detection | ❌ Not in this release (M5, Kubernetes track) |
| Automatic reconciliation loop | ❌ Not in this release (M5, Kubernetes track) |

---

## Applying Config Changes

To apply a configuration change:

```bash
# After committing config changes to Git:
make up
# or:
docker compose up -d --force-recreate
```

In a CI/CD pipeline, trigger `make up` on merge to the main branch. This achieves
continuous delivery of configuration changes without requiring a controller loop.

---

## Consequences

### Positive

- No additional tooling required beyond Docker Compose.
- Simple, understandable deployment model for the target audience.
- Full audit trail of all configuration changes via Git history.
- Pushes to `main` now trigger CI-driven reconciliation (`.github/workflows/deploy.yml`),
  making deployment application deterministic and auditable per commit.
- Grafana provisioning ensures dashboards and datasources cannot be changed through the
  UI without a corresponding commit.

### Negative / Trade-offs

- **Config drift is possible** — If a team member runs `docker compose up` with a
  modified local file, the running state may diverge from the repository. Drift detection
  is manual (compare running container config with repository config).
- **No automatic remediation** — If a service is reconfigured out-of-band (e.g., direct
  container exec), the repository does not detect or correct this.
- **No pull-based drift controller** — Reconciliation is push-triggered in CI, not a
  continuous pull-based controller loop with automatic drift remediation.

### Planned Evolution

- **M5 (planned):** Helm + ArgoCD track for Kubernetes deployments. This track will add
  full pull-based reconciliation, automatic drift detection, and continuous
  synchronisation. The Docker Compose push-triggered track will continue to be maintained.
