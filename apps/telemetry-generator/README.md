# Telemetry Generator

Simple Flask application that generates OpenTelemetry metrics, logs, and traces for testing the observability stack.

## Endpoints

- `GET /` - Health check and service info
- `GET /generate` - Generate telemetry (trace, logs, metrics)
- `GET /error` - Generate error trace/log for testing
- `GET /slow` - Generate slow request (1-3s) for latency testing

## Telemetry Generated

### Traces

- Automatic HTTP spans via Flask instrumentation
- Custom spans for operations
- Span attributes: operation.id, operation.type, duration, error

### Logs

- Structured logs with trace correlation
- INFO: Normal operations
- WARNING: Slow requests
- ERROR: Intentional errors

### Metrics

- `requests_total` (counter): Total requests by endpoint and status
- `processing_duration_seconds` (histogram): Request processing time

The OTel collector's Prometheus exporter applies a `namespace: "app_metrics"` prefix
(see `config/otel/collector.yaml`) to avoid name collisions across instrumented apps.
In Prometheus/Grafana these show up as `app_metrics_requests_total` and
`app_metrics_processing_duration_seconds`.

## Usage

Start the stack (requires the `core` profile too — `apps` alone has no backend to send to):

```bash
make up-apps
# equivalent to: docker compose --profile core --profile apps up -d
```

The app is published on host port **5001** (container port 5000, see `compose.yaml`).

Generate telemetry:

```bash
# Normal request
curl http://localhost:5001/generate

# Generate errors
curl http://localhost:5001/error

# Generate slow traces
curl http://localhost:5001/slow

# Generate load
for i in {1..10}; do curl http://localhost:5001/generate; done
```

## Verification

View in Grafana (http://localhost:3000, default login `admin` / value of `GRAFANA_ADMIN_PASSWORD` in `.env`):

- **Traces:** Explore → Tempo → search `service.name=telemetry-generator`
- **Logs (trace-correlated, from the OTel SDK):** Explore → Loki → `{job="telemetry-generator"}`
- **Logs (raw container stdout, from Alloy):** Explore → Loki → `{compose_service="telemetry-generator"}`
- **Metrics:** Explore → Prometheus → `app_metrics_requests_total`
