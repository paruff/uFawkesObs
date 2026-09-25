---
paths:
  - dashboards/**
---

# dashboards/ Rules

- Grafana dashboard JSON files in `dashboards/platform/` and `dashboards/services/`.
- All datasource UIDs must be string references (e.g. `prometheus`, `tempo`,
  `loki`) — never numeric IDs.
- `schemaVersion` must be 39 (Grafana 12.x).
- UID convention: `ufawkesobs-<slug>`.
- Tags must include `ufawkesobs` for platform dashboards.
