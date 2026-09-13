# uFawkesObs

[![CI](https://github.com/paruff/uFawkesObs/actions/workflows/ci.yml/badge.svg)](https://github.com/paruff/uFawkesObs/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Part of Fawkes IDP](https://img.shields.io/badge/Part%20of-Fawkes%20IDP-purple.svg)](https://github.com/paruff/fawkes)

## What This Is

uFawkesObs is for small-to-medium engineering teams (3–15 people) running Docker Compose workloads who want production-grade metrics, logs, and traces without a SaaS observability bill.

It is a Docker Compose-based observability platform that provides the OpenTelemetry, Prometheus, Loki, Tempo, Alertmanager, Alloy, and Grafana infrastructure needed to collect, store, and query telemetry in one place.

**Tech Stack:** OpenTelemetry Collector · Prometheus · Tempo · Loki · Alloy · Alertmanager · Grafana

**Primary Use Case:** Self-hosted observability foundation deployable with `make up`. Configure secure Grafana credentials in `.env` first.

**Multi-Stack Support:** Designed to serve as a centralized observability platform for multiple Docker Compose applications. See [Multi-Stack Integration Guide](docs/multi-stack-integration.md).

---

## What This Is Not

- Not a DORA metrics generator — it is the instrumentation substrate that makes DORA measurement possible.
- Not a replacement for Grafana Cloud or Datadog for teams with >50 engineers or multi-region deployments.
- Not horizontally scalable in this release — single-instance only.
- Not multi-tenant — all telemetry shares one Prometheus, Loki, and Tempo instance.

---

## Part of the Fawkes IDP

uFawkesObs is the **observability plane** in the [Fawkes IDP](https://github.com/paruff/fawkes) family — a suite of composable platform engineering stacks. The active uFawkes (Docker Compose) suite is Obs, Pipe, DevX, and Dojo, plus [ufawkes.dev](https://ufawkes.dev) as the suite's public site — Fawkes itself is the Kubernetes-track graduation target, not a suite-tier peer. See [When to Graduate to Fawkes](docs/fawkes-migration.md) for that path.

| Plane | Role | Repository |
|---|---|---|
| **uFawkesObs** | Observability — metrics, logs, traces, dashboards | [GitHub](https://github.com/paruff/uFawkesObs) |
| **uFawkesPipe** | CI/CD — pipeline orchestration, deployment events | [GitHub](https://github.com/paruff/ufawkespipe) |
| **uFawkesDevX** | Developer experience — golden paths, IDP templates | [GitHub](https://github.com/paruff/ufawkesdevx) |
| **uFawkesDojo** | Learning — belt-level curriculum for uFawkes and Fawkes | [GitHub](https://github.com/paruff/uFawkesDojo) |

**Not a suite plane — the template used to build all of the above:**

- **uFawkesAI** — an `AGENTS.md`/agent-instruction template (Copilot, Claude Code, Cursor, Codex, etc.) implementing the DORA AI Capabilities Model, not a deployable service. Every repo in the uFawkes/Fawkes family — including this one — is scaffolded from it, which is what "part of the uFawkesAI suite" means in `AGENTS.md` §1: not a runtime dependency, a shared starting template. See [uFawkesAI](https://github.com/paruff/uFawkesAI).

**Retired from the active uFawkes suite** (2026-08-18 product decision):

- **uFawkesRes** — was the resources plane (ingress, SSO, Postgres, Valkey). The [repo](https://github.com/paruff/uFawkesRes) is still real and active, but this repo's `resource-plane` Compose profile has been removed — DORA's datastore is SQLite only, permanently. Anyone wanting a resource plane should target Fawkes (the Kubernetes track) — see [docs/fawkes-migration.md](docs/fawkes-migration.md). See [docs/notes/res-status.md](docs/notes/res-status.md) for the full rationale.
- **DORA metrics** — was uFawkesDORA; merged into uFawkesObs's `dora/` directory. [uFawkesDORA](https://github.com/paruff/ufawkesdora) is archived. See `AGENTS.md` §10.
- **Security — policy-as-code, supply chain, guardrails** — was uFawkesSec; merged into uFawkesPipe's `security` Compose profile (DefectDojo, Infisical, Trivy server, Falco). Per uFawkesPipe's README, this is "formerly the standalone uFawkesSec repo." Note: unlike uFawkesDORA, the [uFawkesSec](https://github.com/paruff/ufawkessec) repo itself has not been archived as of this writing (still receiving dependabot updates) — the merge is confirmed functionally, but the source repo's own lifecycle status is unresolved.

In this architecture, uFawkesObs provides the telemetry substrate consumed by the other **uFawkes (Compose-tier)** planes. The OTLP API (`otel-collector:4317`/`4318`) is how Pipe, DevX and Dojo ship metrics, logs, and traces to uFawkesObs for centralized observability.

**Fawkes is not one of those consumers.** Fawkes is the Kubernetes-track graduation target and runs its own observability stack — kube-prometheus-stack, Tempo, OpenSearch and DevLake — which **replaces uFawkesObs wholesale** rather than consuming it. uFawkesObs is the Compose-tier stepping stone: the stack you run until Kubernetes is worth its operational cost. See [When to Graduate to Fawkes](docs/fawkes-migration.md) for what carries over and what does not.

---

## Quick Start

### Prerequisites

- **Docker** 20.10+ installed
- **Docker Compose** v2.0+ installed
- At least 4GB of free RAM
- Ports 3000, 3100, 3200, 4317, 4318, 8888, 8889, 9090, 9093, 9095, 9096, 9411, 12345, 14250, 14268 available

### Installation

1. **Clone and enter:**

   ```bash
   git clone https://github.com/paruff/uFawkesObs.git
   cd uFawkesObs
   ```

2. **Create and configure environment variables:**

   ```bash
   cp .env.example .env
   $EDITOR .env
   ```

   Set both `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD` in `.env`.

3. **Create data directories and start the stack:**

   ```bash
   make init && make up
   ```

   `make init` creates each `data/` directory with `755` permissions and prints
   the correct `chown` commands for your OS if a container cannot write to a
   directory. See [docs/production-hardening.md](docs/production-hardening.md)
   for details.

4. **Wait for services to become healthy:**
   ```bash
   ./scripts/wait-healthy.sh
   ```

### Key Ports

| Service | Port | Access URL |
|---|---|---|
| **Grafana** | 3000 | http://localhost:3000 |
| **Prometheus** | 9090 | http://localhost:9090 |
| **OTLP gRPC** | 4317 | localhost:4317 |
| **OTLP HTTP** | 4318 | localhost:4318 |

Full port table: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#ports)

### Profiles

| Profile | Services | Purpose |
|---|---|---|
| `core` | otel-collector, tempo, loki, alloy, alertmanager, prometheus, grafana | Base observability stack |
| `apps` | telemetry-generator | Demo telemetry generator |
| `notifications` | alertmanager-discord | Slack/Discord notification bridge (needs `DISCORD_WEBHOOK_URL` in `.env`) |
| `dora` | dora-api, dora-compute, pushgateway, otel-collector-dora | DORA metrics — self-contained, SQLite-only |

```bash
make up                      # core profile
make up-apps                 # add demo telemetry generator
make up-dora                 # add DORA metrics
```

---

## Documentation

| Document | Description |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How services connect and depend on each other |
| [docs/production-hardening.md](docs/production-hardening.md) | Correct permissions, TLS, secret management, when NOT to use this tool |
| [docs/multi-stack-integration.md](docs/multi-stack-integration.md) | Connecting other Docker Compose applications |
| [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) | Known issues and workarounds |
| [docs/CHANGE_IMPACT_MAP.md](docs/CHANGE_IMPACT_MAP.md) | What breaks when configs change |
| [docs/PROMPT_LIBRARY.md](docs/PROMPT_LIBRARY.md) | Tested prompt templates for common tasks |
| [tests/README.md](tests/README.md) | Test pyramid, marker taxonomy, and running tests |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |

---

## Testing

```bash
make up                          # stack must be running first
make test-unit                   # unit tests (no stack needed)
make test-acceptance-smoke       # fast, pre-merge
make test-acceptance-full        # comprehensive, post-merge (SLOs and contracts)
```

See [tests/README.md](tests/README.md) for the full test pyramid and marker taxonomy.

---

## Next Steps

- **DORA data integration:** wire deployment and commit event sources from uFawkesPipe so DORA metrics can be computed from reliable data.
- **Production hardening:** add stronger authentication/TLS posture, storage backends, and operational safeguards for longer-lived deployments.
- **Kubernetes deployment option:** provide a Helm + ArgoCD track for pull-based reconciliation and multi-node operations.

---

## Development Philosophy

This project follows these principles:

- ✅ **GitOps at the configuration layer:** all desired state is in version control and applied declaratively. In this release, deployment reconciliation is push-triggered (via `make up` or CI). Pull-based reconciliation (continuous sync from git to runtime state) requires the Helm + ArgoCD track.
- ✅ **Reproducible:** Can be rebuilt from zero with `git clone` + `make up`
- ✅ **No manual steps:** Zero UI clicks or CLI wizardry required
- ✅ **Declarative:** All configuration is explicit and file-based
- ✅ **Boring technology:** Reliable, well-documented, production-ready tools

---

## License

[Apache License 2.0](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report bugs, suggest
features, and submit pull requests (branch naming, test requirements, and
PR description format).

## Beta Feedback

We're closing in on calling uFawkesObs "beta" and want to hear from real
users first — especially if you starred/forked this repo but never
actually ran it, or you tried it and got stuck. Tell us what happened in
[**Beta Feedback discussion**](https://github.com/paruff/uFawkesObs/discussions/242)
— a sentence is enough.

**Product Suite Roadmap**: [fawkes/ROADMAP.md](https://github.com/paruff/fawkes/blob/main/ROADMAP.md)
