# Multi-Stack Integration Guide

**Audience:** Platform engineers integrating uFawkesPipe, uFawkesDevX, or other planes with uFawkesObs
**Prerequisite:** uFawkesObs core stack running (`docker compose --profile core up -d`)

---

## Overview

uFawkesObs exposes a dedicated Docker bridge network named **`observability-lab`** (internal name: `observability`). External uFawkes planes join this network to send telemetry (traces, metrics, logs) to the centralized observability stack.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Docker Host / VM                                    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    observability-lab (bridge)                       │   │
│   │                                                                     │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│   │  │  Prometheus  │  │     Tempo    │  │     Loki     │  uFawkesObs   │   │
│   │  │   :9090      │  │  :3200/9095  │  │   :3100      │  Core Stack   │   │
│   │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│   │         │                 │                 │                      │   │
│   │  ┌──────┴─────────────────┴─────────────────┴───────┐             │   │
│   │  │           OpenTelemetry Collector                │             │   │
│   │  │           (OTLP :4317/:4318)                     │             │   │
│   │  └────────────────────────────┬────────────────────┘             │   │
│   │                               │                                 │   │
│   │  ┌────────────────────────────┴────────────────────┐             │   │
│   │  │  External Planes (join network)                 │             │   │
│   │  │  • uFawkesPipe  → OTLP → Collector              │             │   │
│   │  │  • uFawkesDevX  → OTLP → Collector              │             │   │
│   │  │  • Custom Apps  → OTLP → Collector              │             │   │
│   │  └─────────────────────────────────────────────────┘             │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │               fawkes-backbone-net (external, M4+)               │  │
│   │  uFawkesRes PostgreSQL  •  uFawkesDORA Ingestion API            │  │
│   └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Quick Start — Join the Observability Network

### Step 1: Start uFawkesObs First

```bash
# In uFawkesObs repo
docker compose --profile core up -d

# Verify health
curl -sf http://localhost:9090/-/healthy   # Prometheus
curl -sf http://localhost:3200/ready       # Tempo
curl -sf http://localhost:3100/ready       # Loki
curl -sf http://localhost:3000/api/health  # Grafana
```

### Step 2: Configure External Plane's Docker Compose

In your plane's `docker-compose.yml` (e.g., uFawkesPipe, uFawkesDevX):

```yaml
services:
  your-service:
    image: your-plane/service:tag
    environment:
      # Point OTLP exporter to uFawkesObs Collector (DNS resolves via Docker network)
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_SERVICE_NAME=your-plane-service-name
    networks:
      - observability

networks:
  observability:
    external: true
    name: observability-lab   # Must match uFawkesObs network name exactly
```

### Step 3: Deploy External Plane

```bash
# In external plane repo
docker compose up -d
```

### Step 4: Verify Telemetry Flow

```bash
# Check traces appear in Tempo (via Grafana)
# Grafana → Explore → Tempo → Search traces by service.name=your-plane-service-name

# Check metrics in Prometheus
curl -s "http://localhost:9090/api/v1/query?query=up{service=\"your-plane-service-name\"}"

# Check logs in Loki
curl -s "http://localhost:3100/loki/api/v1/query?query={service=\"your-plane-service-name\"}"
```

---

## 2. OTLP Endpoint Reference

| Protocol | Host (in-network) | Port | Path |
|---|---|---|---|
| **gRPC** | `otel-collector` | `4317` | — |
| **HTTP** | `otel-collector` | `4318` | `/v1/traces`, `/v1/metrics`, `/v1/logs` |

> **Important:** Use the service name `otel-collector` (not `localhost`). Docker Compose DNS resolves this to the correct container IP within the `observability-lab` network.

---

## 3. Service Name Conventions

To enable correlation in Grafana dashboards, set `OTEL_SERVICE_NAME` consistently:

| Plane | Recommended `OTEL_SERVICE_NAME` Pattern |
|---|---|
| uFawkesPipe | `ufawkespipe`, `ufawkespipe-worker`, `ufawkespipe-controller` |
| uFawkesDevX | `ufawkesdevx`, `ufawkesdevx-agent`, `ufawkesdevx-ide` |
| Custom Apps | `<app-name>-<environment>` (e.g., `orders-api-prod`) |

---

## 4. M4+ DORA/Ecosystem Integration (Backbone Network)

Starting with Milestone 4, external planes also join the **`fawkes-backbone-net`** network to access:

- **uFawkesRes PostgreSQL** — DORA metric snapshots, archetype history, wellbeing surveys
- **uFawkesDORA Ingestion API** — Event forwarding for deployment/incident events

### Extended Network Configuration

```yaml
services:
  your-service:
    image: your-plane/service:tag
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_SERVICE_NAME=your-plane-service-name
      # M4+ DORA event forwarding
      - DORA_INGESTION_URL=http://ufawkesdora-ingestion:8080/events
      - PG_DORA_SNAPSHOTS_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@ufawkesres-postgres:5432/dora_metrics  # pragma: allowlist secret
    networks:
      - observability
      - fawkes-backbone-net

networks:
  observability:
    external: true
    name: observability-lab
  fawkes-backbone-net:
    external: true
    name: ufawkes-resources_fawkes-backbone-net  # Created by uFawkesRes deployment
```

> **Note:** The `fawkes-backbone-net` name includes the Docker Compose project prefix from uFawkesRes (default: `ufawkes-resources_`). Verify with `docker network ls` on the uFawkesRes host.

---

## 5. Reference: docker-compose.integration.yml

uFawkesObs provides a reference template at [`docker-compose.integration.yml`](../docker-compose.integration.yml):

```bash
# View the template
cat docker-compose.integration.yml

# Validate syntax (requires --profile placeholder since no default services)
docker compose -f docker-compose.integration.yml --profile placeholder config
```

**Key sections:**

```yaml
networks:
  observability:
    external: true
    name: observability-lab

  fawkes-backbone-net:
    external: true
    name: ufawkes-resources_fawkes-backbone-net
```

> **Do not deploy this file directly.** Copy the `networks:` block and adapt the example services into your plane's own `docker-compose.yml`.

---

## 6. Troubleshooting

### "Network observability-lab not found"

**Cause:** uFawkesObs core stack not started, or network name mismatch.

**Fix:**
```bash
# 1. Start uFawkesObs
cd /path/to/uFawkesObs && docker compose --profile core up -d

# 2. Verify network exists
docker network ls | grep observability-lab
# Should show: <id>  observability-lab  bridge  local
```

### "Connection refused to otel-collector:4317"

**Cause:** Service not on same network, or Collector not healthy.

**Fix:**
```bash
# 1. Verify both containers on same network
docker network inspect observability-lab --format '{{range .Containers}}{{.Name}} {{end}}'
# Should list: otel-collector, tempo, loki, prometheus, grafana, YOUR-SERVICE

# 2. Check Collector health
docker compose -f /path/to/uFawkesObs/compose.yaml ps otel-collector
# Status should be "healthy"
```

### Traces not appearing in Tempo/Grafana

**Cause:** Wrong `OTEL_SERVICE_NAME`, sampling dropping spans, or Collector pipeline issue.

**Fix:**
```bash
# 1. Check Collector received spans (metrics endpoint)
curl -s http://localhost:8888/metrics | grep otelcol_receiver_accepted_spans

# 2. Verify service.name label in Tempo
# Grafana → Explore → Tempo → {service.name="your-service"}

# 3. Check Collector logs for errors
docker compose -f /path/to/uFawkesObs/compose.yaml logs otel-collector --tail=100
```

### Logs not appearing in Loki

**Cause:** Alloy not scraping, or log format not parsed.

**Fix:**
```bash
# 1. Check Alloy health
curl -s http://localhost:12345/-/ready

# 2. Check Alloy logs for discovery errors
docker compose -f /path/to/uFawkesObs/compose.yaml logs alloy --tail=50

# 3. Query Loki directly
curl -s "http://localhost:3100/loki/api/v1/label/service/values"
# Should include your service name
```

---

## 7. Security Notes

- **No secrets in compose files:** All passwords/tokens via `.env` (gitignored) or external secret manager
- **Network isolation:** `observability-lab` only exposes OTLP (4317/4318), Prometheus (9090), Grafana (3000) to host. Internal inter-service traffic stays on bridge.
- **M4+ backbone:** `fawkes-backbone-net` is a separate network — only planes needing PostgreSQL/DORA API access should join it.

---

## 8. Related Documentation

| Document | Purpose |
|---|---|
| [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) | Full component topology and data flows |
| [`docs/specification.md`](../docs/specification.md) | Functional requirements and interface contracts |
| [`docker-compose.integration.yml`](../docker-compose.integration.yml) | Reference network configuration template |
| [`compose.yaml`](../compose.yaml) | uFawkesObs core stack definition |

---

## 9. Support

- **Issues:** [paruff/uFawkesObs/issues](https://github.com/paruff/uFawkesObs/issues)
- **Architecture questions:** Tag `@paruff/platform-team` in PR discussions
