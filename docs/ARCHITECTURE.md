# Architecture — uFawkesObs

> Read this before changing service dependencies, ports, or network topology.
> Update this file whenever a new service is added, removed, or re-wired.

---

## Services

All services run in the `observability-lab` Docker Compose project on the `observability` network
(Docker network name: `observability-lab`). All core services use the `core` profile.

| Service               | Image                                     | Version | Port(s)                                                                           | Role                                                                              |
| --------------------- | ----------------------------------------- | ------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `otel-collector`      | `otel/opentelemetry-collector-contrib`    | 0.120.0 | 4317 (gRPC), 4318 (HTTP), 8888 (self-metrics), 8889 (Prometheus exporter)         | Receives OTLP telemetry, routes metrics → Prometheus, traces → Tempo, logs → Loki |
| `prometheus`          | `prom/prometheus`                         | v3.5.4  | 9090                                                                              | Stores and queries metrics; scrapes otel-collector and alloy                      |
| `alertmanager`        | `prom/alertmanager`                       | v0.28.0 | 9093                                                                              | Receives alerts from Prometheus, routes notifications                             |
| `tempo`               | `grafana/tempo`                           | 2.10.5  | 3200 (HTTP), 9095 (gRPC), 9411 (Zipkin), 14250 (Jaeger gRPC), 14268 (Jaeger HTTP) | Stores and queries distributed traces                                             |
| `loki`                | `grafana/loki`                            | 3.3.2   | 3100 (HTTP), 9096 (gRPC)                                                          | Stores and queries logs                                                           |
| `alloy`               | `grafana/alloy`                           | v1.12.2 | 12345 (HTTP/metrics)                                                              | Scrapes Docker container logs, forwards to Loki                                   |
| `grafana`             | `grafana/grafana`                         | 12.3.7  | 3000                                                                              | Visualization UI; datasources: Prometheus, Tempo, Loki, Alertmanager              |
| `node-exporter`       | `prom/node-exporter`                      | v1.8.1  | 9100                                                                              | Exposes host-level hardware and OS metrics for Prometheus                         |
| `telemetry-generator` | custom build (`apps/telemetry-generator`) | —       | 5001 (external) / 5000 (internal)                                                 | Demo app that emits OTLP telemetry (profile: `apps`)                              |

---

## Data Flow

```
┌──────────────────────────────────────────────────────┐
│  Applications / Telemetry Generator (apps profile)   │
│  Send OTLP telemetry to otel-collector :4317/:4318   │
└────────────────────────┬─────────────────────────────┘
                         │ OTLP gRPC/HTTP
                         ▼
            ┌────────────────────────┐
            │   OpenTelemetry        │
            │   Collector :4317/4318 │
            └──┬──────────┬─────────┬┘
               │ metrics  │ traces  │ logs
               ▼          ▼         ▼
  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
  │  Prometheus  │  │  Tempo   │  │     Loki     │◄──┐
  │    :9090     │  │  :3200   │  │    :3100     │   │
  └──────┬───────┘  └────┬─────┘  └──────┬───────┘   │
         │ alerts        │               │            │
         ▼               │               │            │
  ┌──────────────┐       │               │            │
  │ Alertmanager │       │               │            │
  │    :9093     │       │               │            │
  └──────────────┘       │               │            │
                         │ datasources   │            │
         ┌───────────────┴───────────────┘            │
         ▼                                            │
  ┌──────────────────────────┐                        │
  │        Grafana           │                        │
  │         :3000            │                        │
  └──────────────────────────┘                        │
                                                      │
  ┌────────────────────┐                              │
  │    Docker Engine   │   container stdout/stderr     │
  │  (container logs)  │──────────────────────────┐   │
  └────────────────────┘                          │   │
                                                  ▼   │
                                           ┌──────────────┐
                                           │    Alloy     │
                                           │   :12345     │
                                           └──────────────┘
```

---

## Service Dependencies

```
grafana       → depends_on: prometheus (healthy)
prometheus    → depends_on: alertmanager
otel-collector→ depends_on: prometheus (healthy), tempo (healthy), loki (healthy)
alloy         → depends_on: loki (healthy)
```

---

## Networks and Volumes

**Network:** All services share `observability` (bridge driver, external name `observability-lab`).

**Named volumes (persistent data):**

| Volume path in container | Host path             | Service      |
| ------------------------ | --------------------- | ------------ |
| `/prometheus`            | `./data/prometheus`   | prometheus   |
| `/var/lib/grafana`       | `./data/grafana`      | grafana      |
| `/var/tempo`             | `./data/tempo`        | tempo        |
| `/loki`                  | `./data/loki`         | loki         |
| `/alertmanager`          | `./data/alertmanager` | alertmanager |
| `/var/lib/alloy`         | `./data/alloy`        | alloy        |

---

## Configuration Files

| Service                | Config path in repo                                        | Mounted at                               |
| ---------------------- | ---------------------------------------------------------- | ---------------------------------------- |
| otel-collector         | `config/otel/collector.yaml`                               | `/etc/otel/collector.yaml`               |
| prometheus             | `config/prometheus/prometheus.yaml`                        | `/etc/prometheus/prometheus.yaml`        |
| prometheus rules       | `config/prometheus/rules/`                                 | `/etc/prometheus/rules/`                 |
| prometheus alerts      | `config/prometheus/alerts.yml`                             | `/etc/prometheus/alerts.yml`             |
| alertmanager           | `config/alertmanager/alertmanager.yml`                     | `/etc/alertmanager/alertmanager.yml`     |
| tempo                  | `config/tempo/tempo.yaml`                                  | `/etc/tempo/tempo.yaml`                  |
| loki                   | `config/loki/loki.yaml`                                    | `/etc/loki/loki.yaml`                    |
| alloy                  | `config/alloy/config.river`                                | `/etc/alloy/config.river`                |
| grafana datasources    | `config/grafana/provisioning/datasources/datasources.yaml` | `/etc/grafana/provisioning/datasources/` |
| grafana dashboards     | `config/grafana/provisioning/dashboards/`                  | `/etc/grafana/provisioning/dashboards/`  |
| grafana dashboard JSON | `config/grafana/dashboards/` and `dashboards/`             | `/var/lib/grafana/dashboards/`           |
| grafana settings       | `config/grafana/grafana.ini`                               | `/etc/grafana/grafana.ini`               |

---

## Profiles

| Profile | Services included                                                                    |
| ------- | ------------------------------------------------------------------------------------ |
| `core`  | otel-collector, tempo, loki, alloy, prometheus, alertmanager, grafana, node-exporter |
| `apps`  | telemetry-generator                                                                  |
| `notifications` | alertmanager-discord (Alertmanager → Discord bridge)                    |
| `dora`  | dora-api, dora-compute, pushgateway, otel-collector-dora (self-contained, SQLite-only) |

Start the full stack:

```bash
docker compose --profile core up -d
```

Start with demo app:

```bash
docker compose --profile core --profile apps up -d
```

Start with Discord notifications enabled (requires `DISCORD_WEBHOOK_URL` in `.env`):

```bash
docker compose --profile core --profile notifications up -d
```

---

## Ports & Access

| Service                 | Port  | Purpose                     | Access URL                    | Published on |
| ------------------------ | ----- | --------------------------- | ------------------------------ | ------------- |
| **Grafana**             | 3000  | Visualization UI            | http://localhost:3000         | all interfaces |
| **Loki**                | 3100  | Log aggregation HTTP API    | http://localhost:3100         | localhost only |
| **Tempo**               | 3200  | Tempo HTTP API              | http://localhost:3200         | localhost only |
| **OpenTelemetry**       | 4317  | OTLP gRPC receiver          | localhost:4317                | all interfaces |
| **OpenTelemetry**       | 4318  | OTLP HTTP receiver          | localhost:4318                | all interfaces |
| **OpenTelemetry**       | 8888  | Collector telemetry metrics | http://localhost:8888/metrics | localhost only |
| **OpenTelemetry**       | 8889  | App metrics (Prometheus)    | http://localhost:8889/metrics | localhost only |
| **Prometheus**          | 9090  | Metrics storage & query UI  | http://localhost:9090         | localhost only |
| **Alertmanager**        | 9093  | Alert management UI         | http://localhost:9093         | localhost only |
| **Tempo**               | 9095  | Tempo gRPC                  | localhost:9095                | localhost only |
| **Loki**                | 9096  | Loki gRPC                   | localhost:9096                | localhost only |
| **node-exporter**       | 9100  | Host-level metrics          | http://localhost:9100/metrics | localhost only |
| **Tempo**               | 9411  | Zipkin receiver             | http://localhost:9411         | localhost only |
| **Alloy**               | 12345 | Alloy HTTP/metrics          | http://localhost:12345        | localhost only |
| **Tempo**               | 14250 | Jaeger gRPC receiver        | localhost:14250               | localhost only |
| **Tempo**               | 14268 | Jaeger HTTP receiver        | http://localhost:14268        | localhost only |
| **Telemetry Generator** | 5001  | Demo app (`apps` profile)   | http://localhost:5001         | all interfaces |
| **DORA API**            | 8088  | DORA ingestion (`dora` profile) | http://localhost:8088     | localhost only |

Only Grafana (3000) and the OTLP ingest endpoints (4317/4318 — other uFawkes
planes ship telemetry here) are published on all interfaces by design. Every
internal/scrape-only port was restricted to localhost per
[#335](https://github.com/paruff/uFawkesObs/issues/335); on a shared or
cloud host, put a reverse proxy with auth in front of Grafana rather than
relying on port binding alone.

**Grafana:** username/password from `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD`
in `.env` (validated by `make check-env`). Prometheus, Tempo, Loki, and
Alertmanager datasources are pre-configured. New to Grafana? Explore
(compass icon, left sidebar) → pick a datasource → query directly — the
fastest way to check if data for a specific service exists before building
a dashboard.

**Alertmanager:** http://localhost:9093 — pre-configured with webhook
receivers for testing; alert rules load automatically from Prometheus.

**Health checks:**

```bash
curl -f http://localhost:9090/-/ready      # Prometheus
curl -f http://localhost:3200/ready        # Tempo
curl -f http://localhost:3000/api/health   # Grafana
curl -f http://localhost:8888/metrics      # OTel Collector telemetry
curl -f http://localhost:3100/ready        # Loki
curl -f http://localhost:12345/-/ready     # Alloy
curl -f http://localhost:9093/-/healthy    # Alertmanager
curl -s http://localhost:9093/api/v2/alerts | jq .   # active alerts
```

Or use the one-shot script: `./scripts/wait-healthy.sh`.

---

## Security Boundaries

- No service exposes credentials in `compose.yaml` — secrets use `.env` (gitignored)
- Grafana admin password is set via `GF_SECURITY_ADMIN_PASSWORD` from `.env`
- All services communicate on the internal `observability` Docker network
- Only explicitly listed ports are bound to `localhost`
- No TLS between internal services (development setup)

---

## See Also

- `docs/CHANGE_IMPACT_MAP.md` — what breaks when a service changes
- `docs/KNOWN_LIMITATIONS.md` — known issues and workarounds
- `config/grafana/provisioning/datasources/datasources.yaml` — Grafana datasource config
- `config/otel/collector.yaml` — OTEL pipeline definitions
