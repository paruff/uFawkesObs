---
name: grafana-provisioning
description: Grafana dashboard JSON and provisioning configuration rules for uFawkesObs. Covers UID-based datasource references, provisioning file structure, and dashboard JSON conventions.
license: MIT
compatibility: opencode
---

# Skill: grafana-provisioning

## Purpose

Grafana dashboard JSON and provisioning configuration rules for uFawkesObs. Covers the critical distinctions between UID-based and numeric datasource references, provisioning file structure, and dashboard JSON conventions.

Load this skill before creating or editing any dashboard JSON or provisioning YAML.

---

## Datasource references — UID only

This is the single most important rule. Numeric datasource IDs are instance-specific — they will be different on every fresh install and will silently break dashboards.

```json
// WRONG — numeric ID, breaks on reinstall
{
  "datasource": {
    "id": 1,
    "type": "prometheus"
  }
}

// CORRECT — UID reference, stable across installs
{
  "datasource": {
    "type": "prometheus",
    "uid": "prometheus"
  }
}
```

### uFawkesObs canonical datasource UIDs

These UIDs are defined in `config/grafana/provisioning/datasources/datasources.yaml` and must be used verbatim in all dashboard JSON.

| Datasource   | uid value      | type         |
| ------------ | -------------- | ------------ |
| Prometheus   | `prometheus`   | prometheus   |
| Loki         | `loki`         | loki         |
| Tempo        | `tempo`        | tempo        |
| Alertmanager | `alertmanager` | alertmanager |

**Verify the UID** before writing: `curl http://localhost:3000/api/datasources` returns the list with UIDs.

---

## Dashboard JSON required fields

Every dashboard JSON file in `dashboards/` must include these fields:

```json
{
  "uid": "ufawkesobs-<slug>",
  "title": "uFawkesObs — <Human Name>",
  "schemaVersion": 39,
  "version": 1,
  "refresh": "30s",
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "panels": [],
  "templating": {
    "list": []
  },
  "annotations": {
    "list": []
  },
  "tags": ["ufawkesobs"]
}
```

**Never include `"id": <number>`** — remove it if it appears (e.g. from an exported dashboard).

**UID naming convention:** `ufawkesobs-<slug>` where slug is kebab-case, e.g.:

- `ufawkesobs-self-monitoring`
- `ufawkesobs-dora-overview`
- `ufawkesobs-ai-metrics`

---

## schemaVersion by Grafana version

| Grafana version      | schemaVersion |
| -------------------- | ------------- |
| 10.4.5 (current)     | 39            |
| 12.x (Wave 4 target) | 40            |

Always check `component-versions` skill before setting schemaVersion.

**Important:** Grafana 12.x disables the numeric datasource ID API entirely. Any dashboard with `"id": <number>` in a datasource reference will fail. Write UID-only from the start.

---

## Provisioning file structure

### Datasources (`config/grafana/provisioning/datasources/datasources.yaml`)

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    uid: prometheus # ← This is the string used in dashboard JSON
    url: http://prometheus:9090
    isDefault: true
    access: proxy
    jsonData:
      timeInterval: "15s"

  - name: Loki
    type: loki
    uid: loki
    url: http://loki:3100
    access: proxy

  - name: Tempo
    type: tempo
    uid: tempo
    url: http://tempo:3200
    access: proxy
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki

  - name: Alertmanager
    type: alertmanager
    uid: alertmanager
    url: http://alertmanager:9093
    access: proxy
```

All `url:` values must use Docker Compose service names, not `localhost`.

### Dashboard provisioner (`config/grafana/provisioning/dashboards/<name>.yaml`)

```yaml
apiVersion: 1
providers:
  - name: uFawkesObs
    orgId: 1
    folder: uFawkesObs
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: false
    options:
      path: /var/lib/grafana/dashboards # Must match compose.yaml volume mount path
```

The `path:` must exactly match the container-side path in the `compose.yaml` volume mount for the grafana service.

---

## Panel conventions

### Time-series panels

```json
{
  "type": "timeseries",
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [
    {
      "expr": "rate(http_requests_total[5m])",
      "legendFormat": "{{job}}",
      "interval": "30s",
      "refId": "A"
    }
  ]
}
```

### Instant/stat panels

```json
{
  "type": "stat",
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [
    {
      "expr": "up{job=\"grafana\"}",
      "instant": true, // ← Required for stat panels
      "refId": "A"
    }
  ]
}
```

### Table panels

```json
{
  "type": "table",
  "targets": [
    {
      "expr": "...",
      "instant": true, // ← Required for tables
      "format": "table",
      "refId": "A"
    }
  ]
}
```

---

## Exporting dashboards safely

When exporting from a running Grafana for version control:

1. Use Grafana UI: Dashboard → Share → Export → Export for sharing externally
2. This replaces numeric datasource IDs with `${DS_PROMETHEUS}` variables — **remove these** and replace with the canonical UID object format above
3. Remove `"id": <number>` from the top-level JSON object
4. Confirm `uid` field is set to the `ufawkesobs-<slug>` convention

---

## Validation

```bash
# Confirm datasources are provisioned and UIDs match
curl http://localhost:3000/api/datasources -u admin:$GRAFANA_ADMIN_PASSWORD

# Confirm dashboards are loaded
curl http://localhost:3000/api/search -u admin:$GRAFANA_ADMIN_PASSWORD | jq '.[].uid'

# Grafana health
curl http://localhost:3000/api/health
```
