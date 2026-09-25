---
paths:
  - config/**
---

# config/ Rules

- Config files are **declarative** — no scripts or logic inside them.
- OpenTelemetry collector config: exporters must match actual running services.
- Prometheus scrape targets must match actual service names in `compose.yaml`.
- Grafana datasources must reference services by Docker Compose service name,
  not `localhost`.
- No credentials in config files — use environment variable substitution
  (`${VAR_NAME}`).
- Alloy River DSL config: use `config.alloy` naming convention.

## Requires a note before merging (AGENTS.md §8)

Any change to Prometheus scrape config requires a note on which metrics will
be affected.
