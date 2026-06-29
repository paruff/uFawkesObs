---
name: obs-stack
description: "Complete uFawkesObs stack reference: service versions, port map, config file locations, Docker Compose operations, and signal flow. Load when configuring, troubleshooting, or extending the uFawkesObs stack."
license: MIT
compatibility: Claude Code, GitHub Copilot, OpenCode, Cursor, Codex, Gemini CLI
metadata:
  author: paruff
  suite: uFawkesObs
---

# Skill: uFawkesObs Stack Reference

## Service Versions and Ports

| Service        | Version  | Internal port        | Host port            | Config file                                      |
| -------------- | -------- | -------------------- | -------------------- | ------------------------------------------------ |
| OTel Collector | 0.120.0  | 4317/4318/8888/8889  | 4317/4318/8888/8889  | `config/otel/collector.yaml`                     |
| Prometheus     | v3.5.4   | 9090                 | 9090                 | `config/prometheus/prometheus.yaml`              |
| Alertmanager   | v0.28.0  | 9093                 | 9093                 | `config/alertmanager/alertmanager.yml`           |
| Tempo          | 2.10.5   | 3200/9095/9411/14250/14268 | 3200/9095/9411/14250/14268 | `config/tempo/tempo.yaml`                |
| Loki           | 3.3.2    | 3100/9096            | 3100/9096             | `config/loki/loki.yaml`                          |
| Alloy          | v1.12.2  | 12345                | 12345                | `config/alloy/config.river`                      |
| Grafana        | 12.3.7   | 3000                 | 3000                 | `config/grafana/` (provisioning)                 |
| Node Exporter  | v1.8.1   | 9100                 | 9100                 | — (no custom config)                             |

## Key Ports by Function

| Port  | Service        | Purpose                                    |
| ----- | -------------- | ------------------------------------------ |
| 4317  | OTel Collector | OTLP gRPC receiver (traces, metrics, logs) |
| 4318  | OTel Collector | OTLP HTTP receiver                         |
| 8888  | OTel Collector | Self-monitoring metrics                    |
| 8889  | OTel Collector | Prometheus exporter (app_metrics namespace)|
| 9090  | Prometheus     | Query API + UI                             |
| 9093  | Alertmanager   | Alert routing UI + API                     |
| 3200  | Tempo          | Trace query API (HTTP)                     |
| 9095  | Tempo          | Trace query API (gRPC)                     |
| 9411  | Tempo          | Zipkin receiver                            |
| 14250 | Tempo          | Jaeger gRPC receiver                       |
| 14268 | Tempo          | Jaeger HTTP receiver                       |
| 3100  | Loki           | Log query API (HTTP)                       |
| 9096  | Loki           | Log query API (gRPC)                       |
| 12345 | Alloy          | HTTP/metrics endpoint                      |
| 3000  | Grafana        | UI + API                                   |
| 9100  | Node Exporter  | Host metrics                               |

## OTel Collector Config Structure

```yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  memory_limiter:        # prevents OOM
    limit_mib: 400
    spike_limit_mib: 100
  batch:                 # improves throughput
    send_batch_size: 10000
    timeout: 10s
  filter/ai:             # AI metrics filter (OBS-AI-01)
    error_mode: ignore
    metrics:
      include:
        match_type: regexp
        metric_names:
          - "gen_ai\\..*"
          - "llm\\..*"
          - "openllmetry\\..*"
          - "ai\\..*"
  attributes/ai:         # AI metric enrichment (OBS-AI-01)
    actions:
      - key: ai.environment
        value: development
        action: insert
      - key: ai.platform
        value: fawkes-idp
        action: insert

exporters:
  debug:                 # verbose logging (development)
    verbosity: normal
  prometheus:            # metrics → Prometheus
    endpoint: "0.0.0.0:8889"
    namespace: app_metrics
    const_labels:
      service: otel-collector
    send_timestamps: true
    metric_expiration: 5m
  otlp/tempo:            # traces → Tempo
    endpoint: tempo:4317
    tls: { insecure: true }
  loki:                  # logs → Loki
    endpoint: http://loki:3100/loki/api/v1/push
    tls: { insecure: true }

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, debug]
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/tempo, debug]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki, debug]
    metrics/ai:
      receivers: [otlp]
      processors: [memory_limiter, filter/ai, attributes/ai, batch]
      exporters: [prometheus]
```

## Prometheus Rule Files

Prometheus loads alerting and recording rules from the mounted `config/prometheus/rules/` directory:

| File                          | Purpose                                      |
| ----------------------------- | -------------------------------------------- |
| `rules/ufawkesobs-self-monitoring.yml` | Self-monitoring alerts for the stack   |
| `rules/ai-rules.yml`          | AI capability recording and alert rules      |

Rules are referenced in `config/prometheus/prometheus.yaml` under `rule_files:`.

## Docker Compose Operations

```bash
# Start core stack (all services except telemetry-generator)
docker compose --profile core up -d

# Start with demo app
docker compose --profile core --profile apps up -d

# Apply config change to one service (no full restart)
docker compose up -d --force-recreate otel-collector

# Apply config change with reload (Prometheus only)
docker compose exec prometheus kill -HUP 1

# View logs for a service
docker compose logs grafana --tail=50 --follow

# Full stop and start (preserves volumes)
docker compose down && docker compose --profile core up -d

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
COMPOSE_PROJECT_NAME=ufawkesobs

# Retention (adjust for disk space)
PROMETHEUS_RETENTION=900d
LOKI_RETENTION=720h         # 30 days
TEMPO_RETENTION=168h        # 7 days

# Alerting (optional — stack runs without these)
ALERTMANAGER_WEBHOOK_URL=   # Slack/PagerDuty webhook
GRAFANA_ADMIN_USER=admin     # default: admin
GRAFANA_ADMIN_PASSWORD=      # default: admin (change in prod)
```

## Telemetry Generator (apps/telemetry-generator/)

Python app that emits test signals to verify the stack end-to-end.

```bash
# Run via Compose (profile: apps)
docker compose --profile core --profile apps up -d

# Run standalone
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

| Backend      | UID            |
| ------------ | -------------- |
| Prometheus   | `prometheus`   |
| Loki         | `loki`         |
| Tempo        | `tempo`        |
| Alertmanager | `alertmanager` |

## Profiles

| Profile | Services included                                                                    |
| ------- | ------------------------------------------------------------------------------------ |
| `core`  | otel-collector, tempo, loki, alloy, prometheus, alertmanager, grafana, node-exporter |
| `apps`  | telemetry-generator                                                                  |

## Related Skills

| Skill          | When to load                                       |
| -------------- | -------------------------------------------------- |
| `otel-collector`  | Editing OTel collector pipelines or processors  |
| `alloy-river`     | Editing Alloy River config for log collection  |
| `promql`          | Writing PromQL recording or alert rules         |
| `alerting`        | Configuring Alertmanager routing and receivers   |
| `dashboard-authoring` | Creating or modifying Grafana dashboards     |
| `grafana-provisioning` | Managing Grafana datasource/dashboard provisioning |
| `dora-metrics`    | DORA metric PromQL expressions                   |
| `otel-semantic-conventions` | OpenTelemetry semantic conventions reference |
