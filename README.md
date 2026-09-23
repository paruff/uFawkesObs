# uFawkesObs

[![CI](https://github.com/paruff/uFawkesObs/actions/workflows/ci.yml/badge.svg)](https://github.com/paruff/uFawkesObs/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Part of Fawkes IDP](https://img.shields.io/badge/Part%20of-Fawkes%20IDP-purple.svg)](https://github.com/paruff/fawkes)

## What This Is

uFawkesObs is for small-to-medium engineering teams (3–15 people) running Docker Compose workloads who want production-grade metrics, logs, and traces without a SaaS observability bill.

It's a Docker Compose stack — OpenTelemetry, Prometheus, Loki, Tempo, Alertmanager, Alloy, and Grafana — that collects, stores, and queries telemetry in one place, deployable with `make up`.

## What This Is Not

- Not a DORA metrics generator — it is the instrumentation substrate that makes DORA measurement possible.
- Not a replacement for Grafana Cloud or Datadog for teams with >50 engineers or multi-region deployments.
- Not horizontally scalable in this release — single-instance only.
- Not multi-tenant — all telemetry shares one Prometheus, Loki, and Tempo instance.

---

## Quick Start

**Prerequisites:** Docker 20.10+, Docker Compose v2.0+, 4GB free RAM, and the ports listed in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#ports--access) available.

```bash
git clone https://github.com/paruff/uFawkesObs.git
cd uFawkesObs

cp .env.example .env
$EDITOR .env   # set GRAFANA_ADMIN_USER and GRAFANA_ADMIN_PASSWORD

make init && make up   # make init sets up data/ dirs with correct permissions
./scripts/wait-healthy.sh
```

Open Grafana at http://localhost:3000. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#ports--access) for every port,
credential, and health-check command, and
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) if something doesn't
come up cleanly.

To run additional profiles (demo telemetry generator, Discord alerts, DORA
metrics), see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#profiles).

---

## Where to Go Next

| Document                                                           | Description                                                            |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)                       | Services, ports, profiles, config file layout, data flow diagram       |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)                 | Port conflicts, permission errors, resetting the stack                 |
| [docs/production-hardening.md](docs/production-hardening.md)       | Correct permissions, TLS, secret management, when NOT to use this tool |
| [docs/multi-stack-integration.md](docs/multi-stack-integration.md) | Connecting other Docker Compose applications                           |
| [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)             | Known issues and workarounds                                           |
| [docs/CHANGE_IMPACT_MAP.md](docs/CHANGE_IMPACT_MAP.md)             | What breaks when configs change                                        |
| [tests/README.md](tests/README.md)                                 | Test pyramid, marker taxonomy, and which suite runs when               |
| [tests/acceptance/README.md](tests/acceptance/README.md)           | How to run the acceptance suite, E2E runner, and unit tests            |
| [docs/PROMPT_LIBRARY.md](docs/PROMPT_LIBRARY.md)                   | Tested prompt templates for common tasks                               |

---

## Part of the Fawkes IDP

uFawkesObs is the **observability plane** in the [Fawkes IDP](https://github.com/paruff/fawkes) family — a suite of composable platform engineering stacks. The active uFawkes (Docker Compose) suite is Obs, Pipe, DevX, and Dojo, plus [ufawkes.dev](https://ufawkes.dev) as the suite's public site — Fawkes itself is the Kubernetes-track graduation target, not a suite-tier peer. See [When to Graduate to Fawkes](docs/fawkes-migration.md) for that path.

| Plane | Role | Repository |
|---|---|---|
| **uFawkesObs** | Observability — metrics, logs, traces, dashboards | [GitHub](https://github.com/paruff/uFawkesObs) |
| **uFawkesPipe** | CI/CD — pipeline orchestration, deployment events | [GitHub](https://github.com/paruff/ufawkespipe) |
| **uFawkesDevX** | Developer experience — golden paths, IDP templates | [GitHub](https://github.com/paruff/ufawkesdevx) |
| **uFawkesDojo** | Learning — belt-level curriculum for uFawkes and Fawkes | [GitHub](https://github.com/paruff/uFawkesDojo) |

Scaffolding template (not a suite plane): **uFawkesAI** — an `AGENTS.md`/agent-instruction template implementing the DORA AI Capabilities Model, used to build every repo above. See [uFawkesAI](https://github.com/paruff/uFawkesAI).

Retired from the active suite (2026-08-18): **uFawkesRes** (resources plane — see [docs/notes/res-status.md](docs/notes/res-status.md)) and standalone **DORA metrics**/**Security** repos, both merged into uFawkesObs/uFawkesPipe respectively. See `AGENTS.md` §10 for detail.

**Fawkes is not a consumer of this repo.** It runs its own Kubernetes-native observability stack and **replaces uFawkesObs wholesale** when a team graduates — see [When to Graduate to Fawkes](docs/fawkes-migration.md) for what carries over.

---

## Development Philosophy

- ✅ **GitOps at the configuration layer** — desired state lives in version control; deployment is currently push-triggered (`make up` or CI). Pull-based reconciliation needs the future Helm + ArgoCD track.
- ✅ **Reproducible** — rebuildable from zero with `git clone` + `make up`
- ✅ **No manual steps** — zero UI clicks or CLI wizardry required
- ✅ **Declarative** — all configuration is explicit and file-based
- ✅ **Boring technology** — reliable, well-documented, production-ready tools

## License

[Apache License 2.0](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report bugs, suggest
features, and submit pull requests. For paid help beyond free community
support, see [SUPPORT.md](SUPPORT.md#work-with-me).

## Beta Feedback

We're closing in on calling uFawkesObs "beta" and want to hear from real
users first — especially if you starred/forked this repo but never
actually ran it, or you tried it and got stuck. Tell us what happened in
[**Beta Feedback discussion**](https://github.com/paruff/uFawkesObs/discussions/242)
— a sentence is enough.
