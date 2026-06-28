# Multi-Stack Integration Guide

## Overview

uFawkesObs is designed as a **centralized observability platform** for multiple Docker Compose applications. Each application stack remains independent but can send telemetry to uFawkesObs.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    uFawkesObs Stack                       │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────┐     │
│  │ OTel         │  │Prometheus│  │   Grafana    │     │
│  │ Collector    │  │          │  │              │     │
│  └──────────────┘  └──────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────┐                        │
│  │    Tempo     │  │   Loki   │                        │
│  └──────────────┘  └──────────┘                        │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ observability-lab network
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │  App    │      │  App    │      │  App    │
   │ Stack 1 │      │ Stack 2 │      │ Stack 3 │
   └─────────┘      └─────────┘      └─────────┘
```

## Integration Pattern

### Step 1: Start uFawkesObs

```bash
cd /path/to/uFawkesObs
docker compose --profile core up -d
```

This creates the `observability-lab` network.

### Step 2: Connect Your Application Stack

In your application's `docker-compose.yml`, add:

```yaml
services:
  your-app:
    # ... your app configuration ...
    networks:
      - default # Your app's internal network
      - observability-lab # uFawkesObs's network
    environment:
      # OpenTelemetry (send to uFawkesObs)
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
      - OTEL_SERVICE_NAME=your-app-name
      - OTEL_TRACES_EXPORTER=otlp
      - OTEL_METRICS_EXPORTER=otlp
      - OTEL_LOGS_EXPORTER=otlp

networks:
  default:
    driver: bridge
  observability-lab:
    external: true
    name: observability-lab
```

### Step 3: Add Prometheus Scrape Job (Optional)

If your app exposes Prometheus metrics, add to uFawkesObs's [`config/prometheus/prometheus.yaml`](../config/prometheus/prometheus.yaml):

```yaml
scrape_configs:
  - job_name: "your-app"
    static_configs:
      - targets: ["your-app-container-name:9090"]
        labels:
          component: "your-app"
          service: "your-service-category"
    scrape_interval: 15s
```

Then restart Prometheus:

```bash
docker compose restart prometheus
```

## Service Endpoints

From your application containers, use these DNS names:

| Service        | Endpoint              | Protocol | Purpose                   |
| -------------- | --------------------- | -------- | ------------------------- |
| OTel Collector | `otel-collector:4317` | gRPC     | OTLP traces/metrics/logs  |
| OTel Collector | `otel-collector:4318` | HTTP     | OTLP traces/metrics/logs  |
| Loki           | `loki:3100`           | HTTP     | Direct log pushing        |
| Tempo          | `tempo:4317`          | gRPC     | Direct trace pushing      |
| Prometheus     | `prometheus:9090`     | HTTP     | Query metrics             |
| Grafana        | `grafana:3000`        | HTTP     | Visualization (if needed) |

## Instrumentation Requirements

### For Applications WITH OpenTelemetry SDK

Set environment variables as shown in Step 2. Your app must use an OpenTelemetry SDK (available for most languages: Go, Python, Java, Node.js, .NET, etc.).

Example for Go:

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
)
```

### For Applications WITHOUT OpenTelemetry SDK

Use **Docker log shipping via Alloy** or Docker logging drivers. Alloy automatically
discovers and ships Docker container logs to Loki — no additional configuration needed
for containers on the `observability-lab` network:

```yaml
services:
  your-app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        tag: "{{.Name}}"
    networks:
      - observability-lab # Join the uFawkesObs network for log collection
```

Once joined to the `observability-lab` network, Alloy will automatically discover and
collect logs from your container.

## Example: Media-Refinery Integration

```yaml
# Media-Refinery's docker-compose.yml
services:
  media-refinery:
    # ... existing config ...
    networks:
      - media-refinery-network
      - observability-lab
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_SERVICE_NAME=media-refinery

networks:
  media-refinery-network:
    driver: bridge
  observability-lab:
    external: true
    name: observability-lab
```

## Kubernetes Integration

Kubernetes-deployed applications can send telemetry to uFawkesObs running on Docker
Compose. Since k8s pods are not on the Docker bridge network by default, you need
to route OTLP traffic through the host network.

### Architecture

```
┌──────────────────────────────────────────────┐
│              Kubernetes Cluster               │
│  ┌────────────┐  ┌────────────┐             │
│  │ Pod (Go)   │  │ Pod (Node) │             │
│  │ OTel SDK   │  │ OTel SDK   │  ...         │
│  └─────┬──────┘  └─────┬──────┘             │
│        │               │                     │
│        └──────┬────────┘                     │
│               │ OTLP HTTP/gRPC               │
└───────────────┼──────────────────────────────┘
                │
                │ host.docker.internal / host IP
                │
┌───────────────▼──────────────────────────────┐
│           Docker Host (same machine)          │
│  ┌──────────────────────────────────────────┐ │
│  │         uFawkesObs Stack                  │ │
│  │  OTel Collector :4318                     │ │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### Approach A: Host Network (Same Machine)

If your Kubernetes cluster runs on the same Docker host as uFawkesObs (e.g.,
kind, k3d, Docker Desktop):

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
        - name: my-app
          image: my-app:latest
          env:
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: "http://host.docker.internal:4318"
            - name: OTEL_EXPORTER_OTLP_PROTOCOL
              value: "http/protobuf"
            - name: OTEL_SERVICE_NAME
              value: "my-app"
            - name: OTEL_RESOURCE_ATTRIBUTES
              value: "k8s.cluster=local,k8s.namespace=default"
```

**Note:** `host.docker.internal` works on macOS and Windows Docker Desktop.
On Linux, use the host's actual IP address or `host.containers.internal`.

### Approach B: NodePort (Different Host)

If Kubernetes and uFawkesObs are on different machines, expose the OTel
Collector HTTP port as a NodePort:

```bash
# On the uFawkesObs host, expose port 4318
docker run -d \
  --name otel-collector-external \
  -p 30418:4318 \
  --network host \
  otel/opentelemetry-collector-contrib:latest
```

Then in your k8s manifests:

```yaml
env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://<ufawkesobs-host-ip>:30418"
```

### Approach C: External DNS

If your uFawkesObs instance has a resolvable DNS name (or you use a service
like ngrok, Tailscale Funnel, or a cloud load balancer):

```yaml
env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://observability.example.com:4318"
```

### Prometheus Scraping from Kubernetes

If you run the Prometheus Operator in your k8s cluster, add a
`PodMonitor` or `ServiceMonitor` pointing to your app's metrics endpoint:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-monitor
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 15s
```

If you scrape directly from uFawkesObs's Prometheus (not recommended for
dynamic k8s environments), add a static target:

```yaml
# config/prometheus/prometheus.yaml
scrape_configs:
  - job_name: "my-app-k8s"
    static_configs:
      - targets: ["<k8s-node-ip>:<node-port>"]
```

---

## Validation

### Network Connectivity (Docker Compose)

From your application container:

```bash
# Test OTel Collector
docker exec your-app-container curl http://otel-collector:4318/

# Test Loki
docker exec your-app-container curl http://loki:3100/ready

# Test Prometheus
docker exec your-app-container curl http://prometheus:9090/-/healthy
```

### Network Connectivity (Kubernetes)

```bash
# From a k8s pod, test connectivity to uFawkesObs
kubectl exec deploy/my-app -- curl -v http://<host>:4318/

# Check the pod can resolve the endpoint
kubectl exec deploy/my-app -- nslookup <host>
```

### Per-Integration Verification Checklist

Use this table to confirm data is flowing for your integration type:

| Integration Type    | Signal  | Where to Check in Grafana                           | Query                                                       |
| ------------------- | ------- | --------------------------------------------------- | ----------------------------------------------------------- |
| Docker Compose      | Traces  | Explore → Tempo datasource                          | `{service.name="your-app"}`                                 |
| Docker Compose      | Logs    | Explore → Loki datasource                           | `{container_name=~".*your-app.*"}`                          |
| Docker Compose      | Metrics | Explore → Prometheus datasource                     | `up{job="your-app"}`                                        |
| Kubernetes (OTel)   | Traces  | Explore → Tempo datasource                          | `{service.name="my-app"}`                                   |
| Kubernetes (OTel)   | Logs    | Explore → Loki datasource                           | `{k8s.namespace="default",k8s.pod=~".*my-app.*"}`           |
| Kubernetes (OTel)   | Metrics | Explore → Prometheus datasource (in-cluster)        | `up{pod=~"my-app-.*"}`                                      |
| Prometheus scrape   | Metrics | Explore → Prometheus datasource                     | `up{job="your-app"}`                                        |
| Alloy auto-logging  | Logs    | Explore → Loki datasource                           | `{container_name=~".*your-app.*"}`                          |
| Plane (any)         | Any     | Infrastructure Overview dashboard → service panel   | Check target appears under the plane's service group        |

### Quick Health Check Script

```bash
#!/bin/bash
# verify-integration.sh - Run from uFawkesObs host

echo "=== OTel Collector ==="
curl -s http://localhost:8888/metrics | grep -c "otelcol_receiver_accepted"
echo "=== Prometheus Targets ==="
curl -s http://localhost:9090/api/v1/targets | grep -c '"health":"up"'
echo "=== Loki Ready ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:3100/ready
echo ""
echo "=== Grafana ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
echo ""
```

## Troubleshooting

### Application can't reach uFawkesObs services

**Problem:** DNS resolution fails or connection refused

**Solution:**

1. Verify network exists: `docker network ls | grep observability-lab`
2. Verify your container joined the network: `docker inspect your-container | grep observability-lab`
3. Restart your application: `docker compose restart`

### No telemetry data appearing

**Problem:** OTel Collector not receiving data

**Checklist:**

- [ ] Application has OpenTelemetry SDK installed and initialized
- [ ] OTEL\_\* environment variables are set correctly
- [ ] Application is on `observability-lab` network
- [ ] OTel Collector is running: `docker ps | grep otel-collector`
- [ ] Check OTel Collector logs: `docker logs otel-collector`

### Logs not appearing in Loki

**Problem:** Logs aren't showing in Grafana

**Solutions:**

- Ensure your container is on the `observability-lab` network (Alloy auto-discovers it)
- Or configure your app to push logs directly via OTLP to `otel-collector:4317`
- Or push logs directly to `loki:3100/loki/api/v1/push`

## Best Practices

1. **Use OpenTelemetry SDK** - Preferred method for traces, metrics, and logs
2. **Keep stacks separate** - Don't merge compose files unless necessary
3. **Use DNS names** - Never use IP addresses or `host.docker.internal`
4. **Label everything** - Use consistent labels for service, environment, etc.
5. **Test in isolation** - Start uFawkesObs first, then your app
6. **Monitor the monitor** - Check uFawkesObs's own telemetry regularly

## Security Considerations

- The `observability-lab` network is **unauthenticated** by default
- Only add trusted applications to this network
- Consider using Docker secrets for sensitive configuration
- For production, add authentication to Grafana, Prometheus, etc.

## Removing an Application

To disconnect an application:

1. Remove `observability-lab` from its networks section
2. Remove OTEL\_\* environment variables
3. Remove Prometheus scrape job (if added)
4. Restart: `docker compose up -d`

The application will continue running but stop sending telemetry.

## Adding More uFawkesObs Components

To add new observability services (e.g., Jaeger, Zipkin):

1. Add service to `compose.yaml`
2. Connect to `observability-lab` network (automatic via default)
3. Update OTel Collector config if needed
4. Restart: `docker compose up -d`

All connected applications automatically gain access to the new service.

---

## Fawkes IDP Plane Integration Patterns

uFawkesObs is part of the [Fawkes IDP](https://github.com/paruff/fawkes) ecosystem.
Other planes join the `observability-lab` network using the same pattern as any Docker
Compose application, but with plane-specific considerations.

### Plane Overview

| Plane           | Repository                  | Role            | Telemetry Type                                                  |
| --------------- | --------------------------- | --------------- | --------------------------------------------------------------- |
| **uFawkesObs**  | `paruff/uFawkesObs`         | Observability   | Metrics, logs, traces, dashboards                               |
| **uFawkesRes**  | `paruff/uFawkesRes`         | Resources       | Infrastructure health, ingress metrics, SSO audit logs          |
| **uFawkesPipe** | `paruff/ufawkespipe`        | CI/CD           | Jenkins pipeline traces, deployment events, build metrics       |
| **uFawkesDevX** | `paruff/ufawkesdevx`        | Developer tools | Local service metrics, development logs, dev environment traces |
| **uFawkesDORA** | `paruff/ufawkesdora`        | DORA metrics    | DORA computation logs, ingestion API metrics, deployment events |

### Integration Pattern for Any Fawkes Plane

All Fawkes planes follow the same Docker Compose integration pattern:

1. **Start uFawkesObs first** (creates the `observability-lab` network)
2. **Join the network** by adding `observability-lab: external: true` to the plane's compose file
3. **Set OTEL environment variables** on services that emit telemetry
4. **Add Prometheus scrape jobs** if the plane exposes a `/metrics` endpoint

```yaml
# In the plane's docker-compose.yml
services:
  plane-service:
    networks:
      - plane-network
      - observability-lab
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
      - OTEL_SERVICE_NAME=plane-service-name
      - OTEL_RESOURCE_ATTRIBUTES=service.namespace=<plane-name>,service.version=1.0.0

networks:
  plane-network:
    driver: bridge
  observability-lab:
    external: true
    name: observability-lab
```

### Plane-Specific Guides

| Plane         | Integration Guide                                                 | Key Considerations                                                             |
| ------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| uFawkesPipe   | [uFawkesPipe Integration](examples/uFawkesPipe-integration.md)   | Jenkins OTEL plugin, pipeline span instrumentation, deployment events for DORA |
| uFawkesDevX   | [uFawkesDevX Integration](examples/uFawkesDevX-integration.md)   | Grafana panel embedding, developer portal access, local service metrics        |
| uFawkesRes    | _(uses uFawkesObs as standard OTLP consumer)_                    | Infrastructure health metrics, SSO audit logs via Alloy                        |
| uFawkesDORA   | _(connects to uFawkesObs Grafana for dashboards)_                | DORA computation metrics via Postgres → Grafana, ingestion API logs            |

### Cross-Plane Change Impact

When modifying uFawkesObs, check the impact on connected planes:

| Change in uFawkesObs                     | Impact                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| OTEL Collector receiver port (4317/4318) | uFawkesPipe Jenkins traces; uFawkesDevX local service traces             |
| Network name in `compose.yaml`           | All planes must update their external network reference                  |
| Prometheus scrape config                 | Any plane with a custom scrape job must be updated                       |
| Grafana admin credentials                | uFawkesDevX developer portal panels; uFawkesDORA dashboard embeds        |
| Grafana datasource UIDs                  | Embedded panels (uFawkesDevX, uFawkesDORA) referencing old IDs will break |

See `docs/CHANGE_IMPACT_MAP.md` for the full cross-plane impact matrix.

### Telemetry Routing by Plane

| Signal                  | Source        | Route                       | Destination          |
| ----------------------- | ------------- | --------------------------- | -------------------- |
| Jenkins pipeline traces | uFawkesPipe   | OTel Collector → Tempo      | Tempo (traces)       |
| Jenkins build metrics   | uFawkesPipe   | OTel Collector → Prometheus | Prometheus (metrics) |
| Jenkins logs            | uFawkesPipe   | Alloy auto-discovery        | Loki (logs)          |
| Dev service metrics     | uFawkesDevX   | OTel Collector → Prometheus | Prometheus (metrics) |
| Dev service logs        | uFawkesDevX   | Alloy auto-discovery        | Loki (logs)          |
| Dev service traces      | uFawkesDevX   | OTel Collector → Tempo      | Tempo (traces)       |
| Infrastructure metrics  | uFawkesRes    | Direct Prometheus scrape    | Prometheus (metrics) |
| SSO audit logs          | uFawkesRes    | Alloy auto-discovery        | Loki (logs)          |
| DORA compute metrics    | uFawkesDORA   | Postgres → Grafana          | Grafana (dashboards) |

### Backstage Catalog Registration

All Fawkes planes should be registered in the parent
[fawkes Backstage catalog](https://github.com/paruff/fawkes). See `catalog-info.yaml`
in each plane's repository root for the entity definition.

uFawkesObs registers as:

- **System:** `ufawkesobs` (observability plane)
- **Components:** One per service (otel-collector, prometheus, tempo, loki, alloy, grafana, alertmanager, node-exporter)
- **API:** `ufawkesobs-otlp` (OTLP endpoint for external consumers)
- **Resources:** Prometheus, Tempo, Loki, Alertmanager instances

---

## Lite / Minimal Startup for Small Teams

### Do I need other stacks?

**No.** uFawkesObs is fully self-contained. It does not require uFawkesPipe,
uFawkesDevX, or any other plane to function. A small team can start with
just uFawkesObs and get immediate value from its built-in dashboards.

### Standard Startup (Core Profile)

```bash
cd /path/to/uFawkesObs
make up
```

This starts all 8 core services — the full observability stack including
metrics (Prometheus), logs (Loki), traces (Tempo), and visualization
(Grafana). ~4 GB RAM minimum.

### Metrics-Only Startup (Minimal)

If you only need metrics and don't require log aggregation or distributed
tracing, start only Prometheus and Grafana:

```bash
# Start just the metrics stack
docker compose up -d prometheus grafana
```

This runs 2 containers instead of 8. ~1 GB RAM.

### Minimal + OTel Collector

If you want to receive OTLP telemetry from external applications but don't
need Loki/Tempo storage:

```bash
docker compose up -d otel-collector prometheus grafana
```

The OTel Collector will forward metrics to Prometheus, and you can drop
traces/logs at the collector level if you don't want to store them. ~1.5 GB RAM.

### What About a Dedicated `minimal` Profile?

A `minimal` compose profile (Prometheus + Grafana + OTel Collector) is a
planned enhancement. Currently, use the manual service selection approach
above. Once a `minimal` profile is added, it will work as:

```bash
docker compose --profile minimal up -d   # Future
```

### Scaling Up

As your team grows and needs more signals:

1. **Add Loki + Alloy** for centralized log aggregation
2. **Add Tempo** for distributed tracing
3. **Add Alertmanager** for alert routing
4. **Connect uFawkesPipe** for CI/CD observability and DORA metrics
5. **Connect uFawkesDORA** for DORA performance dashboards
