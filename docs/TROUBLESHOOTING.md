# Troubleshooting — uFawkesObs

> Permission and UID issues in particular are covered in depth in
> [docs/production-hardening.md](production-hardening.md) — this doc covers
> the rest.

## Ports already in use

```bash
# Check what's using the ports
lsof -i :3000
lsof -i :9090

# Either stop the conflicting service or modify compose.yaml port mappings
```

## Permission denied on data directories

Run `make init` first — it creates each directory with `755` permissions
and prints the correct `chown` commands for your OS:

```bash
make init
```

If a container still cannot write (common on Linux when the host UID
differs from the container UID), apply the `chown` commands printed by
`make init`, for example:

```bash
sudo chown -R 472 data/grafana          # Grafana UID
sudo chown -R 65534 data/prometheus data/alertmanager  # nobody UID
sudo chown -R 10001 data/loki data/tempo               # Loki/Tempo UID
```

> **⚠️ Last resort — security warning:** `chmod -R 777 data/` makes every
> data directory world-writable. This exposes Prometheus TSDB, Grafana
> SQLite, datasource credentials, and trace data to any process on the
> host. Only use this on a single-user localhost machine and never in any
> shared or networked environment. See
> [docs/production-hardening.md](production-hardening.md) for secure
> alternatives.

## Containers won't start

```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs grafana
```

## Reset everything

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

> **⚠️ Last resort only:** If `make init` is insufficient due to a UID
> mismatch, you may temporarily use `chmod -R 777 data/` on a single-user
> localhost machine. This is a security risk — see
> [docs/production-hardening.md](production-hardening.md).

## See Also

- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — ports, access, health checks
- [docs/KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) — known issues and workarounds
- [SUPPORT.md](../SUPPORT.md) — where to ask if this doesn't cover it
