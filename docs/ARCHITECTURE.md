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
| `prometheus`          | `prom/prometheus`                         | v2.55.1 | 9090                                                                              | Stores and queries metrics; scrapes otel-collector and alloy                      |
| `alertmanager`        | `prom/alertmanager`                       | v0.27.0 | 9093                                                                              | Receives alerts from Prometheus, routes notifications                             |
| `tempo`               | `grafana/tempo`                           | 2.10.5  | 3200 (HTTP), 9095 (gRPC), 9411 (Zipkin), 14250 (Jaeger gRPC), 14268 (Jaeger HTTP) | Stores and queries distributed traces                                             |
| `loki`                | `grafana/loki`                            | 2.9.10  | 3100 (HTTP), 9096 (gRPC)                                                          | Stores and queries logs                                                           |
| `alloy`               | `grafana/alloy`                           | v1.12.2 | 12345 (HTTP/metrics)                                                              | Scrapes Docker container logs, forwards to Loki                                   |
| `grafana`             | `grafana/grafana`                         | 10.4.5  | 3000                                                                              | Visualization UI; datasources: Prometheus, Tempo, Loki, Alertmanager              |
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
alloy         → depends_on: loki (healthy), prometheus (healthy)
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

Start the full stack:

```bash
docker compose --profile core up -d
```

Start with demo app:

```bash
docker compose --profile core --profile apps up -d
```

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
