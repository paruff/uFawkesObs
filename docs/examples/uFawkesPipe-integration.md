# uFawkesPipe (deliveryd) → uFawkesObs Integration Guide

## Overview

uFawkesPipe is the CI/CD plane of the Fawkes IDP family. It orchestrates Jenkins pipelines
and generates deployment events. This guide connects uFawkesPipe's telemetry to uFawkesObs
so that pipeline traces, Jenkins metrics, and deployment events flow into the centralized
observability platform.

**What you get after integration:**

- Jenkins pipeline execution traces in Tempo
- Jenkins metrics (build duration, success rate, queue depth) in Prometheus
- Jenkins logs in Loki via Alloy auto-discovery
- Deployment events available for DORA metrics computation (Phase 5)

---

## Architecture

```
┌──────────────────────────────────────────────┐
│           uFawkesPipe (deliveryd)            │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Jenkins  │  │ Pipeline │  │ OTEL      │ │
│  │ Master   │  │ Events   │  │ SDK       │ │
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
- uFawkesPipe (deliveryd) running with Jenkins
- Both stacks on the same Docker host (or connected via the `observability-lab` network)

---

## Step 1: Connect uFawkesPipe to the Observability Network

In uFawkesPipe's `docker-compose.yml`, add the `observability-lab` network to any service
that needs to send telemetry:

```yaml
services:
  jenkins:
    # ... existing config ...
    networks:
      - uFawkesPipe-network
      - observability-lab

  # Add to any other services that emit telemetry:
  pipeline-runner:
    # ... existing config ...
    networks:
      - uFawkesPipe-network
      - observability-lab

networks:
  uFawkesPipe-network:
    driver: bridge
  observability-lab:
    external: true
    name: observability-lab
```

---

## Step 2: Configure OTEL Environment Variables

Add OpenTelemetry environment variables to Jenkins or any pipeline runner that should emit
traces and metrics:

```yaml
services:
  jenkins:
    # ... existing config ...
    environment:
      # ... existing env vars ...
      # OpenTelemetry — send to uFawkesObs
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
      - OTEL_SERVICE_NAME=jenkins
      - OTEL_RESOURCE_ATTRIBUTES=service.namespace=deliveryd,service.version=1.0.0
      - OTEL_TRACES_EXPORTER=otlp
      - OTEL_METRICS_EXPORTER=otlp
      - OTEL_LOGS_EXPORTER=otlp
```

### Jenkins OTEL Plugin (Recommended)

The easiest way to instrument Jenkins is with the
[OpenTelemetry Jenkins Plugin](https://github.com/jenkinsci/opentelemetry-plugin):

1. Install the plugin via Jenkins → Manage Jenkins → Plugins
2. Configure the OTLP exporter endpoint: `http://otel-collector:4318`
3. Set the service name: `jenkins`
4. Enable trace export for pipeline executions

This automatically generates spans for each pipeline stage and exports them to Tempo.

### Alternative: Java OTEL Agent

If not using the Jenkins plugin, attach the Java OTEL agent to Jenkins:

```yaml
services:
  jenkins:
    environment:
      - JAVA_TOOL_OPTIONS=-javaagent:/opt/opentelemetry/javaagent.jar
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_SERVICE_NAME=jenkins
```

Mount the agent JAR into the container:

```yaml
volumes:
  - ./opentelemetry-javaagent.jar:/opt/opentelemetry/javaagent.jar:ro
```

---

## Step 3: Configure Jenkins Pipeline Events

To emit deployment events for DORA metrics, instrument your Jenkinsfile with OTEL spans:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    // Custom span for deployment event
                    sh '''
                        curl -X POST http://otel-collector:4318/v1/traces \
                          -H "Content-Type: application/json" \
                          -d '{
                            "resourceSpans": [{
                              "resource": {
                                "attributes": [
                                  {"key": "service.name", "value": {"stringValue": "jenkins"}},
                                  {"key": "deployment.environment", "value": {"stringValue": "production"}}
                                ]
                              },
                              "scopeSpans": [{
                                "scope": {"name": "jenkins-pipeline"},
                                "spans": [{
                                  "name": "deploy",
                                  "kind": 1,
                                  "attributes": [
                                    {"key": "deployment.trigger", "value": {"stringValue": "pipeline"}},
                                    {"key": "deployment.target", "value": {"stringValue": "production"}}
                                  ]
                                }]
                              }]
                            }]
                          }'
                    '''
                }
            }
        }
    }
}
```

---

## Step 4: Add Prometheus Scrape Job for Jenkins

If Jenkins exposes Prometheus metrics (via the
[Prometheus Metrics plugin](https://plugins.jenkins.io/prometheus/)):

Add to uFawkesObs's `config/prometheus/prometheus.yaml`:

```yaml
scrape_configs:
  # ... existing jobs ...

  # Jenkins metrics
  - job_name: 'jenkins'
    static_configs:
      - targets: ['jenkins:8080']
        labels:
          component: 'jenkins'
          service: 'deliveryd'
    metrics_path: '/prometheus'
    scrape_interval: 15s
```

Restart Prometheus:

```bash
cd /path/to/uFawkesObs
docker compose restart prometheus
```

---

## Step 5: Verify Integration

### Network Connectivity

```bash
# From Jenkins container, verify OTel Collector is reachable
docker exec jenkins curl -v http://otel-collector:4318/

# Verify Prometheus is reachable
docker exec jenkins curl -v http://prometheus:9090/-/healthy
```

### Telemetry Flow

```bash
# Check OTel Collector is receiving Jenkins telemetry
curl http://localhost:8888/metrics | grep -i jenkins

# Check Prometheus targets
curl 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.component=="jenkins")'

# Check Tempo for traces
curl 'http://localhost:3200/api/traces?service=jenkins' | jq
```

### Grafana Verification

1. Open Grafana at http://localhost:3000
2. **Logs:** Explore → Loki → query `{container_name="jenkins"}`
3. **Traces:** Explore → Tempo → search by service name `jenkins`
4. **Metrics:** Explore → Prometheus → query `up{component="jenkins"}`

---

## Troubleshooting

### Jenkins container can't resolve 'otel-collector'

**Cause:** Jenkins container not on `observability-lab` network.

```bash
docker inspect jenkins | grep -A 20 Networks
# Should show both uFawkesPipe-network and observability-lab

# If missing, recreate:
docker compose up -d --force-recreate jenkins
```

### No traces in Tempo

**Cause:** OTEL plugin not installed or not configured correctly.

```bash
# Check Jenkins logs for OTEL errors
docker logs jenkins 2>&1 | grep -i "opentelemetry\|otel\|otlp"

# Verify OTel Collector is receiving traces
curl http://localhost:8888/metrics | grep traces_received
```

### No Jenkins metrics in Prometheus

**Cause:** Prometheus Metrics plugin not installed or scrape target down.

```bash
# Check Prometheus targets page
curl 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.job_name=="jenkins")'
# Should show state: "up"
```

---

## Service Endpoints Reference

| Service | Endpoint | Protocol | Purpose |
|---|---|---|---|
| OTel Collector | `otel-collector:4317` | gRPC | OTLP traces/metrics/logs |
| OTel Collector | `otel-collector:4318` | HTTP | OTLP traces/metrics/logs |
| Prometheus | `prometheus:9090` | HTTP | Query Jenkins metrics |
| Loki | `loki:3100` | HTTP | Query Jenkins logs |
| Tempo | `tempo:3200` | HTTP | Query Jenkins traces |
| Grafana | `grafana:3000` | HTTP | Visualization |

---

## Cross-Plane Impact

When modifying uFawkesObs to support uFawkesPipe integration, check:

| Change in uFawkesObs | Impact on uFawkesPipe |
|---|---|
| OTEL Collector receiver port (4317/4318) | Jenkins OTEL plugin endpoint must be updated |
| Network name in `compose.yaml` | uFawkesPipe must join the updated network |
| Prometheus scrape config | Jenkins scrape job must be updated |

See `docs/CHANGE_IMPACT_MAP.md` for the full cross-plane impact matrix.

---

## Next Steps

1. **DORA integration:** Wire deployment events from Jenkins pipelines to uFawkesObs for
   DORA metrics computation (see Phase 5, issue #80)
2. **Custom dashboards:** Create Grafana dashboards for Jenkins pipeline metrics
3. **Alerting:** Add Prometheus alerts for failed builds, slow pipelines, queue depth
4. **Add other CI services:** Use the same pattern for build agents, artifact stores, etc.
