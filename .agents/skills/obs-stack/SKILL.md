---
name: obs-stack
description: "Complete Obstackd stack reference: service versions, port map, config file locations, Docker Compose operations, and signal flow. Load when configuring, troubleshooting, or extending the uFawkesObs stack."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesObs
---

# Skill: Obstackd Stack Reference

## Service Versions and Ports

| Service | Version | Internal port | Host port | Config file |
|---|---|---|---|---|
| OTel Collector | v0.103.1 | 4317/4318/8888/13133 | 4317/4318/8888/13133 | `config/otel-collector-config.yaml` |
| Prometheus | v2.52.0 | 9090 | 9090 | `config/prometheus.yml` + `config/prometheus-rules/` |
| Alertmanager | v0.27.0 | 9093 | 9093 | `config/alertmanager.yml` |
| Tempo | v2.5.0 | 3200/9095 | 3200 | `config/tempo-config.yaml` |
| Loki | v2.9.10 | 3100 | 3100 | `config/loki-config.yaml` |
| Alloy | v1.12.2 | 12345 | 12345 | `config/alloy-config.alloy` |
| Grafana | v10.4.5 | 3000 | 3000 | `config/grafana/` |

## Key Ports by Function

| Port | Service | Purpose |
|---|---|---|
| 4318 | OTel Collector | OTLP HTTP receiver (traces, metrics, logs) |
| 4317 | OTel Collector | OTLP gRPC receiver |
| 8888 | OTel Collector | Self-monitoring metrics |
| 13133 | OTel Collector | Health check endpoint |
| 9090 | Prometheus | Query API + UI |
| 9093 | Alertmanager | Alert routing UI + API |
| 3200 | Tempo | Trace query API |
| 3100 | Loki | Log query API |
| 3000 | Grafana | UI + API |

## OTel Collector Config Structure

```yaml
receivers:
  otlp:           # accepts OTLP from any service
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }
  prometheus:     # scrapes /metrics endpoints
    config:
      scrape_configs: [...]

processors:
  batch: {}       # improves throughput
  memory_limiter: # prevents OOM
    limit_mib: 400

exporters:
  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write
  otlp/tempo:
    endpoint: http://tempo:4317
    tls: { insecure: true }
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/tempo]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki]
```

## Docker Compose Operations

```bash
# Start stack
docker compose up -d

# Apply config change to one service (no full restart)
docker compose up -d --force-recreate otel-collector

# View logs for a service
docker compose logs grafana --tail=50 --follow

# Full stop and start (preserves volumes)
docker compose down && docker compose up -d

# Destroy everything including volumes (DATA LOSS)
docker compose down -v

# Check all service health
for svc in otel-collector prometheus alertmanager tempo loki grafana; do
  echo -n "$svc: "
  docker compose ps $svc --format "{{.Status}}"
done
```

## Environment Variables (.env)

Required in `.env` (gitignored, see `.env.example`):

```bash
# Stack identity
ENVIRONMENT=dev             # dev | staging | prod
COMPOSE_PROJECT_NAME=obstackd

# Retention (adjust for disk space)
PROMETHEUS_RETENTION=15d
LOKI_RETENTION=168h         # 7 days
TEMPO_RETENTION=72h         # 3 days

# Alerting (optional — stack runs without these)
ALERTMANAGER_WEBHOOK_URL=   # Slack/PagerDuty webhook
GRAFANA_ADMIN_PASSWORD=     # default: admin (change in prod)
```

## Telemetry Generator (apps/telemetry-generator/)

Python app that emits test signals to verify the stack end-to-end.

```bash
# Run the generator
cd apps/telemetry-generator
pip install -r requirements.txt
OTEL_SERVICE_NAME=telemetry-generator \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 \
python main.py
```

Verify it worked:
- Metrics: `http://localhost:9090/graph?g0.expr=up{job="telemetry-generator"}`
- Traces: Grafana → Explore → Tempo → search service=telemetry-generator
- Logs: Grafana → Explore → Loki → `{service="telemetry-generator"}`

## Grafana Datasource UIDs

Always use these UIDs in dashboard JSON:

| Backend | UID |
|---|---|
| Prometheus | `prometheus` |
| Loki | `loki` |
| Tempo | `tempo` |
| Alertmanager | `alertmanager` |