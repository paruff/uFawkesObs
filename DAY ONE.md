# Day One with uFawkesObs

You've just cloned the repo. This guide covers the next 30 minutes: what
you'll run, what you'll see, and where to go next. It assumes you've already
completed the Quick Start in the README (`make init && make up`).

---

## What just started

`make up` started seven services:

| Service | What it does | Where to find it |
|---|---|---|
| **OpenTelemetry Collector** | Receives telemetry from your apps and routes it | `localhost:4317` (gRPC), `localhost:4318` (HTTP) |
| **Prometheus** | Stores and queries metrics | `localhost:9090` |
| **Alertmanager** | Manages and routes alerts | `localhost:9093` |
| **Loki** | Stores and queries logs | `localhost:3100` |
| **Tempo** | Stores and queries traces | `localhost:3200` |
| **Alloy** | Collects container logs from Docker Engine | `localhost:12345` |
| **Grafana** | Visualizes everything | `localhost:3000` |

All datasources (Prometheus, Loki, Tempo, Alertmanager) are pre-configured.
You do not need to add them manually.

---

## Step 1 — Confirm everything is healthy

```bash
./scripts/wait-healthy.sh
```

Expected output: all services reporting healthy. If a service fails, check
`docker compose logs <service-name>` — permission errors on `./data/` are
the most common cause. Run `make init` if you skipped it.

---

## Step 2 — Open Grafana and look around

Open <http://localhost:3000> and log in with the credentials from your `.env` file.

**Things to try:**

1. **Explore → Prometheus**: Run the query `up` — you should see a 1 for each
   platform service being scraped.

2. **Explore → Loki**: Run `{job="docker"}` — you'll see container log streams
   from the running stack itself.

3. **Explore → Tempo**: If you've already sent a trace (see Step 3), you can
   search for it here.

4. **Alertmanager**: Open <http://localhost:9093> — the pre-configured webhook
   receivers are visible under Status → Config.

---

## Step 3 — Send some real telemetry

Start the bundled telemetry generator to see the full pipeline with data:

```bash
docker compose --profile apps up -d telemetry-generator
```

Wait about 30 seconds, then in Grafana:

- **Prometheus → Explore**: Run `http_requests_total` — you'll see metrics
  from the generator
- **Loki → Explore**: Run `{service_name="telemetry-generator"}` — structured logs
- **Tempo → Explore**: Search for traces from `telemetry-generator`

When you're done:

```bash
docker compose --profile apps stop telemetry-generator
```

---

## Step 4 — Connect your own application

Your application sends telemetry to the OTel Collector. The collector is
reachable at:

- **gRPC**: `localhost:4317` (or `otel-collector:4317` from within Docker Compose)
- **HTTP**: `localhost:4318` (or `otel-collector:4318` from within Docker Compose)

Configure your OTel SDK exporter to point there. For cross-stack Docker Compose
setups (your application in a separate `compose.yaml`), see
[docs/multi-stack-integration.md](./docs/multi-stack-integration.md) — it
covers the network configuration needed to connect across compose projects.

---

## Step 5 — Understand the configuration files

All configuration is in `config/`:

```
config/
├── otel/collector.yaml          ← What the collector accepts and where it routes
├── prometheus/prometheus.yaml   ← What Prometheus scrapes
├── grafana/provisioning/        ← Pre-configured datasources (do not edit manually)
├── alertmanager/alertmanager.yml ← Where alerts are sent
├── loki/loki.yaml               ← Log retention and storage
└── tempo/tempo.yaml             ← Trace retention and storage
```

The unit tests (`pytest tests/unit/`) validate all of these files. Run them
before committing any config change:

```bash
pip install -r tests/unit/requirements.txt
pytest tests/unit/
```

---

## What this stack does not do (yet)

- **DORA metrics**: uFawkesObs provides the substrate. Calculated DORA dashboards
  live in [uFawkesDORA](https://github.com/paruff/ufawkesdora), which wires in
  deployment and commit events from [uFawkesPipe](https://github.com/paruff/ufawkespipe).
- **Multi-tenancy**: All telemetry shares one instance. See
  [docs/KNOWN_LIMITATIONS.md](./docs/KNOWN_LIMITATIONS.md).
- **TLS**: Default config is localhost-only plaintext. See
  [docs/production-hardening.md](./docs/production-hardening.md) before
  exposing any port.

---

## Where to go next

| I want to… | Go here |
|---|---|
| Connect another Docker Compose app | [docs/multi-stack-integration.md](./docs/multi-stack-integration.md) |
| Harden for a shared environment | [docs/production-hardening.md](./docs/production-hardening.md) |
| Understand the architecture | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) |
| Add a Prometheus alert rule | [config/prometheus/](./config/prometheus/) + run `pytest tests/unit/test_prometheus_config_validation.py` |
| Add DORA metrics | [uFawkesDORA](https://github.com/paruff/ufawkesdora) |
| Report a bug | [GitHub Issues](https://github.com/paruff/uFawkesObs/issues) |
| Ask a question | [GitHub Discussions](https://github.com/paruff/uFawkesObs/discussions) |
| Contribute a change | [CONTRIBUTING.md](./CONTRIBUTING.md) |

---

## Stopping and cleaning up

```bash
# Stop all services, keep data
docker compose down

# Stop and remove all data (full reset)
docker compose down -v
rm -rf data/prometheus/* data/grafana/* data/tempo/* data/loki/* data/alertmanager/* data/alloy/*
make init
```
