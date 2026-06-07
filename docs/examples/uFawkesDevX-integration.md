# uFawkesDevX (developerd) → uFawkesObs Integration Guide

## Overview

uFawkesDevX is the developer plane of the Fawkes IDP family. It provides local development
workflows, tooling, and developer environment management. This guide connects uFawkesDevX's
telemetry to uFawkesObs so that developer tool logs, local service metrics, and development
events are visible in the centralized observability platform.

**What you get after integration:**

- Developer tool logs in Loki via Alloy auto-discovery
- Local service metrics in Prometheus (if instrumented with /metrics endpoint)
- Development environment traces in Tempo (if instrumented with OTel SDK)
- Unified visibility across development and production environments

---

## Architecture

```
┌──────────────────────────────────────────────┐
│           uFawkesDevX (developerd)           │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Dev      │  │ Local    │  │ OTEL      │ │
│  │ Tools    │  │ Services │  │ SDK       │ │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘ │
│       │              │              │        │
└───────┼──────────────┼──────────────┼────────┘
        │              │              │
        │  observability-lab network  │
        │              │              │
┌───────▼──────────────▼──────────────▼────────┐
│              uFawkesObs                       │
│  ┌──────────────┐  ┌──────────┐  ┌────────┐ │
│  │ OTel         │  │Prometheus│  │ Grafana│ │
│  │ Collector    │  │          │  │        │ │
│  └──────────────┘  └──────────┘  └────────┘ │
│  ┌──────────────┐  ┌──────────┐              │
│  │    Tempo     │  │   Loki   │              │
│  └──────────────┘  └──────────┘              │
└──────────────────────────────────────────────┘
```

---

## Prerequisites

- uFawkesObs running with `docker compose --profile core up -d`
- uFawkesDevX (developerd) running with local development services
- Both stacks on the same Docker host (or connected via the `observability-lab` network)

---

## Step 1: Connect uFawkesDevX to the Observability Network

In uFawkesDevX's `docker-compose.yml`, add the `observability-lab` network to services
that should emit telemetry:

```yaml
services:
  # Example: development database, API server, etc.
  dev-api:
    # ... existing config ...
    networks:
      - uFawkesDevX-network
      - observability-lab

  dev-database:
    # ... existing config ...
    networks:
      - uFawkesDevX-network
      - observability-lab

networks:
  uFawkesDevX-network:
    driver: bridge
  observability-lab:
    external: true
    name: observability-lab
```

**Important:** Only add services that should send telemetry to uFawkesObs. The developer
tools themselves (IDEs, CLI tools) typically run on the host, not in containers.

---

## Step 2: Configure OTEL Environment Variables

Add OpenTelemetry environment variables to any containerized service that should emit
traces, metrics, or logs:

```yaml
services:
  dev-api:
    # ... existing config ...
    environment:
      # ... existing env vars ...
      # OpenTelemetry — send to uFawkesObs
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
      - OTEL_SERVICE_NAME=dev-api
      - OTEL_RESOURCE_ATTRIBUTES=service.namespace=developerd,service.version=dev
      - OTEL_TRACES_EXPORTER=otlp
      - OTEL_METRICS_EXPORTER=otlp
      - OTEL_LOGS_EXPORTER=otlp
```

### Language-Specific Setup

**Go:**
```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
)
```
See: [OpenTelemetry Go Getting Started](https://opentelemetry.io/docs/languages/go/getting-started/)

**Python:**
```bash
pip install opentelemetry-distro
opentelemetry-bootstrap -a install
```
See: [OpenTelemetry Python Getting Started](https://opentelemetry.io/docs/languages/python/getting-started/)

**Node.js:**
```bash
npm install @opentelemetry/sdk-node
```
See: [OpenTelemetry JS Getting Started](https://opentelemetry.io/docs/languages/js/getting-started/)

**Java:**
```bash
# Attach Java agent
-javaagent:/path/to/opentelemetry-javaagent.jar
```
See: [OpenTelemetry Java Getting Started](https://opentelemetry.io/docs/languages/java/getting-started/)

---

## Step 3: Auto-Collect Logs via Alloy

Any container on the `observability-lab` network has its logs automatically collected by
Alloy and shipped to Loki. No additional configuration is needed.

For containers without OTel SDK instrumentation, logs are still collected:

```yaml
services:
  dev-service:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        tag: "{{.Name}}"
    networks:
      - observability-lab  # Alloy auto-discovers and ships logs
```

---

## Step 4: Add Prometheus Scrape Job (Optional)

If your development services expose Prometheus metrics endpoints:

Add to uFawkesObs's `config/prometheus/prometheus.yaml`:

```yaml
scrape_configs:
  # ... existing jobs ...

  # Development API metrics
  - job_name: 'dev-api'
    static_configs:
      - targets: ['dev-api:8080']
        labels:
          component: 'dev-api'
          service: 'developerd'
    scrape_interval: 15s
    metrics_path: '/metrics'
    scheme: 'http'
```

Restart Prometheus:

```bash
cd /path/to/uFawkesObs
docker compose restart prometheus
```

---

## Step 5: Grafana Access for Developers

Developers can access Grafana dashboards to debug issues:

```bash
# Open Grafana
open http://localhost:3000

# Login with credentials from .env
# Default: admin / admin (change in .env before sharing)
```

### Embedding Grafana Panels (Advanced)

If uFawkesDevX needs to embed Grafana panels in a developer portal or dashboard:

```yaml
services:
  dev-portal:
    environment:
      # Grafana embed URL pattern
      - GRAFANA_URL=http://grafana:3000
      # Use datasource UIDs (not numeric IDs) for stable references
      - GRAFANA_DS_PROMETHEUS=prometheus
      - GRAFANA_DS_LOKI=loki
```

**Note:** The Grafana admin credentials format is documented in `docs/KNOWN_LIMITATIONS.md`.
If uFawkesDevX embeds Grafana panels, it must use the same credential format.

---

## Step 6: Verify Integration

### Network Connectivity

```bash
# From a dev service container, verify OTel Collector is reachable
docker exec dev-api curl -v http://otel-collector:4318/

# Verify Loki is reachable
docker exec dev-api curl -v http://loki:3100/ready
```

### Telemetry Flow

```bash
# Check OTel Collector is receiving dev telemetry
curl http://localhost:8888/metrics | grep -i "dev-api\|developerd"

# Check Prometheus targets
curl 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.service=="developerd")'

# Check Loki for dev logs
curl 'http://localhost:3100/loki/api/v1/query?query={service_name="dev-api"}' | jq
```

### Grafana Verification

1. **Logs:** Explore → Loki → query `{container_name=~"dev-.*"}`
2. **Traces:** Explore → Tempo → search by service name `dev-api`
3. **Metrics:** Explore → Prometheus → query `up{service="developerd"}`

---

## Troubleshooting

### Dev containers can't resolve 'otel-collector'

**Cause:** Container not on `observability-lab` network.

```bash
docker inspect dev-api | grep -A 20 Networks
# Should show both uFawkesDevX-network and observability-lab

# If missing, recreate:
docker compose up -d --force-recreate dev-api
```

### No logs in Grafana

**Cause:** Container not on `observability-lab` network.

```bash
# Verify the container joined the network
docker network inspect observability-lab | grep dev-api

# If missing, add the network and recreate:
docker compose up -d --force-recreate dev-api
```

### No traces visible

**Cause:** Application doesn't have OTel SDK instrumentation.

Logs and metrics may still work via Alloy auto-discovery and Prometheus scraping.
Traces require explicit OTel SDK instrumentation in application code.

---

## Service Endpoints Reference

| Service | Endpoint | Protocol | Purpose |
|---|---|---|---|
| OTel Collector | `otel-collector:4317` | gRPC | OTLP traces/metrics/logs |
| OTel Collector | `otel-collector:4318` | HTTP | OTLP traces/metrics/logs |
| Prometheus | `prometheus:9090` | HTTP | Query dev metrics |
| Loki | `loki:3100` | HTTP | Query dev logs |
| Tempo | `tempo:3200` | HTTP | Query dev traces |
| Grafana | `grafana:3000` | HTTP | Visualization |

---

## Cross-Plane Impact

When modifying uFawkesObs to support uFawkesDevX integration, check:

| Change in uFawkesObs | Impact on uFawkesDevX |
|---|---|
| Grafana admin credentials format | Developer tooling that embeds Grafana panels must use updated credentials |
| Network name in `compose.yaml` | uFawkesDevX must join the updated network |
| Grafana datasource UIDs | Embedded panels referencing old numeric IDs will break |

See `docs/CHANGE_IMPACT_MAP.md` for the full cross-plane impact matrix.

---

## Next Steps

1. **Custom dashboards:** Create Grafana dashboards for development service metrics
2. **Alerting:** Add Prometheus alerts for dev environment health (high error rate, slow response)
3. **Developer portal integration:** Embed Grafana panels in developer portal UI
4. **DORA integration:** Wire development events to uFawkesObs for DORA metrics (see Phase 5, #80)
