# ADR-002: Docker Compose as the Primary Deployment Runtime

**Status:** Accepted  
**Date:** 2025-06-01  
**Deciders:** uFawkesObs maintainers  
**Issue:** [M1-02](https://github.com/paruff/uFawkesObs/issues/68)

---

## Context

Observability platforms are commonly deployed on Kubernetes (Helm charts, Operators, or
managed services such as Grafana Cloud). Kubernetes provides high availability, horizontal
scaling, native secret management, and an ecosystem of mature GitOps controllers (ArgoCD,
Flux). It is also significantly more complex to operate.

uFawkesObs targets small engineering teams (3–15 people) running workloads on a single
VM or a small number of VMs. These teams typically do not have a Kubernetes cluster, a
cluster administrator, or the operational overhead budget that Kubernetes requires.
Asking this audience to provision and manage a Kubernetes cluster as a prerequisite for
deploying an observability stack is a higher barrier than the problem it solves.

---

## Decision

**Use Docker Compose as the primary deployment runtime** for uFawkesObs v0.1.x.

All services (Prometheus, Loki, Tempo, Grafana, OTEL Collector, Alloy, Alertmanager) are
defined in a single `compose.yaml`. Deployment is a single `make up` or
`docker compose up -d` command.

---

## Rationale

1. **Target audience match** — Small teams on single VMs have Docker installed. They may
   not have Kubernetes. Docker Compose is the lowest-friction path to a running
   observability stack.

2. **Operational simplicity** — Docker Compose requires no control plane, no cluster
   administration, no persistent volume provisioner, and no ingress controller. The full
   stack runs and recovers from a single `docker compose up`.

3. **Lowest barrier to adoption** — The primary goal of v0.1.x is for teams to have
   working observability in under 15 minutes. Docker Compose achieves this; Kubernetes
   does not.

4. **Additive Kubernetes path** — A Kubernetes deployment track (Helm charts) is planned
   for Milestone 5 (M5). It is an additive option for teams that have already adopted
   Kubernetes, not a replacement for the Docker Compose track. The two tracks will coexist.

5. **Honest scope boundary** — Documenting Docker Compose as a deliberate scope decision
   prevents adopters from mistaking a capability boundary for a capability gap. Teams who
   need HA or horizontal scaling know immediately that they should wait for the M5 track
   or self-adapt the stack.

---

## Consequences

### Positive

- Single-command deployment and teardown.
- No Kubernetes prerequisite or cluster administration burden.
- Configuration is portable: `compose.yaml` + `config/` directory is the complete
  desired state.
- Suitable for CI/CD pipelines, developer laptops, and single-VM production environments.

### Negative / Trade-offs

- **No high availability (HA)** — If the host VM goes down, the entire observability
  stack goes down. There is no failover.
- **No horizontal scaling** — All services are single-instance. Prometheus, Loki, and
  Tempo cannot be horizontally scaled within Docker Compose.
- **No Kubernetes-native secret management** — Secrets (Grafana admin credentials) are
  managed via `.env` file. There is no integration with Vault, AWS Secrets Manager, or
  Kubernetes Secrets in this track.
- **No native controller loop** — Config changes require a manual `make up` or CI push
  trigger. There is no pull-based reconciliation (see ADR-003).

### Planned Evolution

- **M5 (planned):** Helm chart track for Kubernetes deployments. This track will add HA,
  horizontal scaling, and Kubernetes-native secret management. The Docker Compose track
  will continue to be maintained.

---

## Alternatives Considered

### Kubernetes + Helm (rejected for v0.1.x)

Adding a Kubernetes prerequisite excludes the primary target audience (small teams on
single VMs). Helm chart complexity increases the time-to-first-working-stack from minutes
to hours. Deferred to M5.

### Docker Swarm (rejected)

Docker Swarm provides multi-host orchestration but is not widely adopted and lacks the
ecosystem of tooling (secrets management, GitOps controllers) that would justify the
added complexity over single-host Docker Compose.
