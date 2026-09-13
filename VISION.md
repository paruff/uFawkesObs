# VISION.md — uFawkesObs

> **Horizon:** Years | **Owner:** Maintainer | **Review:** Quarterly
> **Feeds into:** [`MILESTONES.md`](MILESTONES.md) → [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) → [`plan-for-the-day.md`](plan-for-the-day.md)

---

## North Star

**Every small engineering team (3–15 people) running Docker Compose gets production-grade observability — metrics, logs, traces, and alerting — without a SaaS bill or a multi-week integration effort.**

uFawkesObs composes the same OSS components those vendors build on (Prometheus, Loki, Tempo, Grafana, OTel Collector, Alertmanager), pre-wired and pre-provisioned, so a small team gets close to the vendor's default experience without the vendor's invoice.

---

## Core Principles

1. **Composition Over Compilation.** Service definitions, volumes, networks, and environment bindings are orchestrated via a centralized, decoupled `compose.yaml` using explicit profiles. No custom operators, no CRDs, no compiled binaries between the user and their telemetry.

2. **GitOps Reconciliation.** Changes to `config/**`, `compose.yaml`, `.env.example`, and `dashboards/**` are auto-reconciled on target environments by GHA-triggered workflows over SSH. The repo is the source of truth; manual edits to running services are transient.

3. **Hot Configuration Reloading.** Config-only updates use native runtime signaling (Prometheus `/-/reload`, Alloy `SIGHUP`) to prevent container downtime. The stack stays available while its configuration evolves.

4. **Self-Monitoring.** Every telemetry service exposes a `/metrics` target scraped by Prometheus. The observability substrate is itself observable — if it breaks, you know before your users do.

5. **Reproducible Local Simulation.** All integration and unit tests run fully locally without external infrastructure or cluster dependencies. A contributor can validate a change with `make test` before pushing.

6. **Discovery Before Build.** Every feature starts with a discovery brief that names the riskiest assumption and an acceptance criterion. No resources committed until the brief is approved. (This principle was violated for M2–M4; `docs/product/discovery-draft.md` is a retrospective audit, not a gating artifact.)

---

## Explicit Non-Goals (Late Beta)

These are out of scope for the current maturity stage. They may become goals later, but not now:

- **Multi-tenancy.** All telemetry shares one instance. Single-team, single-cluster only.
- **Horizontal scaling.** Single-instance deployment. No sharding, no federation, no load-balanced read replicas.
- **Kubernetes-native deployment.** M5 is a migration path to the Fawkes K8s track — not an active uFawkesObs gate. Docker Compose is the target runtime for late beta.
- **Production TLS between internal services.** Localhost-only plaintext is the default. TLS is a production-hardening concern documented in `docs/production-hardening.md`, not a beta requirement.
- **Multi-host progressive delivery.** Canary/staging/load-balanced production is aspirational (`docs/DEPLOYMENT_STRATEGY.md`), not a beta gate.
- **Secret management substrate.** Vault/uFawkesSec owns root credentials. uFawkesObs consumes secrets via `.env` injection only.

---

## Riskiest Assumption

> A 3–15 person team will accept operating its own observability infrastructure
> (upgrades, disk growth, backup, on-call for the stack itself) in exchange for
> not paying a SaaS bill.

**Status:** Named, not yet tested. See `docs/product/discovery-draft.md` § "Honest Limitations" for what this assumption does *not* establish. The onboarding-speed sub-claim has been validated (93s, PASS); the operational-burden risk remains open.

---

## How This Connects

| Document | Horizon | What It Answers |
|---|---|---|
| [`MILESTONES.md`](MILESTONES.md) | Months | What are we building next, and in what order? |
| [`EXECUTION_QUEUE.md`](EXECUTION_QUEUE.md) | Weeks | What specific tasks are ready to be worked? |
| [`plan-for-the-day.md`](plan-for-the-day.md) | Today | What am I doing right now? |
| [`docs/product/discovery-draft.md`](docs/product/discovery-draft.md) | Discovery | Why does this product exist? What's the riskiest assumption? |
| [`docs/product/spec.md`](docs/product/spec.md) | Spec | What are the functional requirements and interface contracts? |
| [`docs/product/design.md`](docs/product/design.md) | Design | How is the architecture structured? What are the design principles? |
| [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md) | Known gaps | Where could the riskiest assumption break first? |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Topology | How do services connect and depend on each other? |
| [`docs/CHANGE_IMPACT_MAP.md`](docs/CHANGE_IMPACT_MAP.md) | Impact | What breaks when a service config changes? |
| [`docs/CONTRACTS.md`](docs/CONTRACTS.md) | Contracts | What does uFawkesObs receive from other planes? |
| [`docs/AI_STANCE.md`](docs/AI_STANCE.md) | Governance | What's this repo's stance on AI-assisted development? |
| [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md) | Release | How do merged commits become a versioned release? |
| [`docs/DEPLOYMENT_STRATEGY.md`](docs/DEPLOYMENT_STRATEGY.md) | Deployment | How does a release reach the running stack, and what's the target model? |
