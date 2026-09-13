# Troubleshooting — uFawkesObs

Common issues and solutions for running uFawkesObs locally.

---

## Ports Already in Use

If you see port binding errors:

```bash
# Check what's using the ports
lsof -i :3000
lsof -i :9090

# Either stop the conflicting service or modify compose.yaml port mappings
```

---

## Permission Denied on Data Directories

Run `make init` first — it creates each directory with `755` permissions and
prints the correct `chown` commands for your OS:

```bash
make init
```

If a container still cannot write (common on Linux when the host UID differs
from the container UID), apply the `chown` commands printed by `make init`, for
example:

```bash
sudo chown -R 472 data/grafana          # Grafana UID
sudo chown -R 65534 data/prometheus data/alertmanager  # nobody UID
sudo chown -R 10001 data/loki data/tempo               # Loki/Tempo UID
```

> **⚠️ Last resort — security warning:** `chmod -R 777 data/` makes every data
> directory world-writable. This exposes Prometheus TSDB, Grafana SQLite,
> datasource credentials, and trace data to any process on the host. Only use
> this on a single-user localhost machine and never in any shared or networked
> environment. See [docs/production-hardening.md](production-hardening.md)
> for secure alternatives.

---

## Containers Won't Start

```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs grafana
```

---

## Reset Everything

```bash
# Stop and remove everything
docker compose down -v

# Clean data directories
rm -rf data/prometheus/* data/grafana/* data/tempo/* data/loki/* data/alertmanager/* data/alloy/*

# Recreate with correct permissions
make init

# Start fresh
make up
```

> **⚠️ Last resort only:** If `make init` is insufficient due to a UID mismatch,
> you may temporarily use `chmod -R 777 data/` on a single-user localhost machine.
> This is a security risk — see [docs/production-hardening.md](production-hardening.md).

---

## Health Checks

Verify that all services are operational:

```bash
# Check Prometheus
curl -f http://localhost:9090/-/ready

# Check Tempo
curl -f http://localhost:3200/ready

# Check Grafana
curl -f http://localhost:3000/api/health

# Check OpenTelemetry Collector telemetry
curl -f http://localhost:8888/metrics

# Check OpenTelemetry Collector app metrics endpoint
curl -f http://localhost:8889/metrics

# Check Loki
curl -f http://localhost:3100/ready

# Check Alloy
curl -f http://localhost:12345/-/ready

# Check Alertmanager
curl -f http://localhost:9093/-/healthy

# View active alerts
curl -s http://localhost:9093/api/v2/alerts | jq .
```

---

## Acceptance Test Failures

If tests fail, check:

1. **Services Running**: `docker compose ps`
2. **OTel Metrics**: `curl http://localhost:8888/metrics | grep otelcol`
3. **Prometheus Target**: http://localhost:9090/targets
4. **Grafana Health**: `curl http://localhost:3000/api/health`
