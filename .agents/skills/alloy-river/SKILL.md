---
name: alloy-river
description: Grafana Alloy River configuration syntax reference for uFawkesObs. Covers the River DSL, Docker container log discovery, label manipulation, and hot-reload compatibility constraints.
license: MIT
compatibility: opencode
---

# Skill: alloy-river

## Purpose

Grafana Alloy River configuration syntax reference for uFawkesObs. Covers the River DSL, Docker container log discovery, label manipulation, and hot-reload compatibility constraints.

Load this skill before editing `config/alloy/config.river`.

---

## River language basics

River is a declarative, block-based configuration language used by Grafana Alloy. It is not YAML, not HCL, not JSON.

### Block syntax

```river
// Block: <namespace>.<component_type> "<label>" { ... }
// Label is optional for singleton components

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

### Attribute syntax

```river
// Attributes: key = value
// Strings use double quotes
// References use component.label.attribute notation

forward_to = [loki.write.default.receiver]   // Reference to another component's export
host       = "unix:///var/run/docker.sock"   // String value
```

### Comments

```river
// Single-line comment only — no /* */ block comments
```

---

## uFawkesObs standard Alloy pipeline

```river
// 1. Discover Docker containers
discovery.docker "all" {
  host = "unix:///var/run/docker.sock"
}

// 2. Relabel: extract container name as a log label
discovery.relabel "containers" {
  targets = discovery.docker.all.targets

  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = "/(.*)"             // Strip leading slash
    target_label  = "container"
  }

  rule {
    source_labels = ["__meta_docker_container_label_com_docker_compose_service"]
    target_label  = "service"           // Add compose service name as label
  }
}

// 3. Collect logs from discovered containers
loki.source.docker "containers" {
  host       = "unix:///var/run/docker.sock"
  targets    = discovery.relabel.containers.output
  forward_to = [loki.write.default.receiver]
}

// 4. Send logs to Loki
loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"    // Docker Compose service name
  }
}
```

---

## Docker labels available for relabeling

When using `discovery.docker`, these `__meta_docker_*` labels are available:

| Label                                                      | Value                                      |
| ---------------------------------------------------------- | ------------------------------------------ |
| `__meta_docker_container_name`                             | Container name (with leading `/`)          |
| `__meta_docker_container_id`                               | Full container ID                          |
| `__meta_docker_container_image`                            | Image name and tag                         |
| `__meta_docker_container_status`                           | `running`, `paused`, etc.                  |
| `__meta_docker_container_label_<key>`                      | Any Docker label (dots become underscores) |
| `__meta_docker_container_label_com_docker_compose_service` | Compose service name                       |
| `__meta_docker_container_label_com_docker_compose_project` | Compose project name                       |

Always use `__meta_docker_container_name` with a regex `/(.*)` to strip the leading slash. Using the raw value with the slash will produce logs with `container="/grafana"` instead of `container="grafana"`.

---

## Hot-reload compatibility

Alloy supports hot-reload via `POST http://localhost:12345/-/reload`. Not all config changes are hot-reloadable.

### Hot-reload compatible (no restart required)

- `loki.source.docker` — adding/removing/changing parameters
- `loki.write` — changing endpoint URL or headers
- `discovery.docker` — changing host or refresh interval
- `discovery.relabel` — adding/modifying relabel rules
- `prometheus.scrape` — adding/changing scrape targets
- `prometheus.remote_write` — changing endpoint

### Requires full restart (flag to Planning agent)

- `logging` block — changing log level or format
- `tracing` block — if present, any change
- Adding a new component type not previously present (sometimes)

### Testing hot-reload

```bash
# Send reload signal
curl -X POST http://localhost:12345/-/reload

# Expected: HTTP 200 with body: configuration reload succeeded
# On failure: HTTP 400 with error details

# Verify config loaded correctly
curl http://localhost:12345/-/ready
```

---

## Docker socket access requirement

Alloy needs access to `/var/run/docker.sock` to use `discovery.docker` and `loki.source.docker`. This must be mounted in `compose.yaml`:

```yaml
services:
  alloy:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro # ro = read-only is sufficient
```

Before adding Docker discovery to the River config, verify this mount exists:

```bash
docker compose config | grep docker.sock
```

If the mount is absent, do not add Docker discovery — flag to Planning agent to update `compose.yaml` first.

---

## Prometheus scraping from Alloy

Alloy can also scrape Prometheus metrics and forward them:

```river
prometheus.scrape "otel_collector" {
  targets = [{"__address__" = "otel-collector:8889"}]   // Docker service name
  forward_to = [prometheus.remote_write.default.receiver]
}

prometheus.remote_write "default" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}
```

This is an alternative to Prometheus scraping directly. In uFawkesObs, Prometheus handles its own scraping — Alloy focuses on logs unless explicitly directed otherwise.

---

## Common errors

| Error                                               | Cause                                   | Fix                                           |
| --------------------------------------------------- | --------------------------------------- | --------------------------------------------- |
| `permission denied /var/run/docker.sock`            | Socket not mounted or wrong permissions | Add volume mount to compose.yaml              |
| Container label `container="/grafana"` (with slash) | Missing regex strip                     | Use `regex = "/(.*)"` in relabel rule         |
| Logs not appearing in Loki                          | `forward_to` points to wrong component  | Check component label matches exactly         |
| `connection refused loki:3100`                      | Loki not yet healthy at startup         | Alloy retries — wait 30s, check loki health   |
| Hot-reload returns 400                              | River syntax error                      | Check Alloy logs: `docker compose logs alloy` |

---

## Validation sequence

```bash
# 1. Alloy is ready
curl http://localhost:12345/-/ready

# 2. After any config change — test hot-reload
curl -X POST http://localhost:12345/-/reload

# 3. Confirm logs are flowing to Loki
curl http://localhost:3100/loki/api/v1/labels | jq '.data'
# Expected: ["container", "filename", "job", "service", ...]

# 4. Check Alloy's own metrics (Prometheus scrapes these)
curl http://localhost:12345/metrics | grep alloy_
```
