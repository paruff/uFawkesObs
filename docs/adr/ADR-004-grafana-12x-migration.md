# ADR-004: Upgrade Grafana from 10.4.5 to 12.3.7

**Status:** Accepted
**Date:** 2026-06-28
**Deciders:** uFawkesObs maintainers
**Issue:** [M1-03](https://github.com/paruff/uFawkesObs/issues/68)

---

## Context

uFawkesObs was initially deployed with Grafana 10.4.5 (`grafana/grafana:10.4.5`). By June
2026, Grafana 12.x was the current stable major version, and Grafana 10.x had reached
end-of-life. Running a version three major versions behind the current release carried
increasing risk:

1. **Security vulnerabilities** — EOL versions no longer receive security patches.
2. **Feature gap** — Grafana 11 introduced a new alerting UI, transformed dashboard
   architecture, and dropped AngularJS plugin support. Grafana 12 added performance
   improvements and panel plugin API v2.
3. **Plugin compatibility** — New plugins increasingly require Grafana 11+.
4. **Observability ecosystem alignment** — Other uFawkes suite components (Prometheus,
   Loki, Tempo) were being upgraded to their latest versions; Grafana needed to follow.

The upgrade from 10.4.5 → 12.3.7 required passing through the Grafana 11 breaking changes
(primarily the removal of AngularJS plugin support) and the Grafana 12 API refinements.

---

## Decision

**Upgrade Grafana from 10.4.5 to 12.3.7** (`grafana/grafana:12.3.7`).

No provisioning configuration changes were required — the existing YAML-based datasource
and dashboard provisioning configuration is fully compatible with Grafana 12.x.

---

## Migration Summary

| Detail              | Value                                                    |
| ------------------- | -------------------------------------------------------- |
| **Previous version** | `grafana/grafana:10.4.5`                                 |
| **Current version**  | `grafana/grafana:12.3.7`                                 |
| **PR**               | N/A (version bump in `compose.yaml` without separate PR) |
| **Date**             | 2026-06-28                                               |
| **Jump**             | 10.4.5 → 12.3.7 (two major versions)                    |
| **Config changes**   | None — existing provisioning config fully compatible     |

### Breaking Changes Assessed and Handled

| Breaking Change                     | Version | Impact on uFawkesObs |
| ----------------------------------- | ------- | -------------------- |
| AngularJS plugin removal            | 11.x    | None — no Angular plugins used |
| Dashboard live (alpha) removal      | 11.x    | None — not used       |
| Alerting UI unification             | 11.x    | None — alerts defined in Prometheus, not Grafana |
| Panel plugin API v2                 | 12.x    | None — all dashboards use built-in panels |
| SQL-based dashboard provisioning removal | 11.x | None — file-based provisioning only |
| Legacy alerting removal             | 11.x    | None — alerts managed via Prometheus + Alertmanager |

### Provisioning Compatibility

All provisioning is file-based and unchanged:

- **Datasources:** `config/grafana/provisioning/datasources/datasources.yaml` —
  Prometheus, Tempo, Loki, Alertmanager. All use `uid`-based references, compatible
  with Grafana 12.x.
- **Dashboards:** `config/grafana/provisioning/dashboards/dashboards.yaml` — loads
  dashboards from `config/grafana/dashboards/` and `dashboards/`. Compatible with
  Grafana 12.x.
- **Configuration:** `config/grafana/grafana.ini` — standard ini format, compatible
  with Grafana 12.x.

---

## Rationale

1. **Security** — Grafana 10.x is EOL and no longer receives security patches. Running
   an EOL version in an observability stack that handles telemetry data is an
   unacceptable risk posture.

2. **Feature availability** — Grafana 11+ provides the new alerting UI, transformed
   dashboard architecture, and faster query performance. These features will be
   required for upcoming milestones (DORA dashboards in M4, AI observability in MAI).

3. **Ecosystem alignment** — All other uFawkesObs components had been upgraded to
   current versions. Grafana was the only service running an EOL version.

4. **No migration effort required** — uFawkesObs does not use Angular plugins, legacy
   alerting, or SQL provisioning. The upgrade was a clean image version bump with no
   configuration changes, making it a low-risk change.

5. **Future-proofing** — Starting from 12.3.7 means the next major upgrade will be from
   a current stable version rather than from an EOL version, reducing migration effort.

---

## Consequences

### Positive

- Running a supported, security-patched version of Grafana.
- Access to Grafana 11+ features: new alerting UI, improved dashboard panel types,
  faster query engine.
- No provisioning or dashboard migration work was required.
- Future upgrades (12.x → 13.x) will be incremental rather than multi-version jumps.

### Negative / Trade-offs

- Grafana 12.x has higher baseline resource requirements than 10.4.5 (expect ~10-15%
   more memory usage for the same dashboard load).
- Some community plugins may not yet support Grafana 12.x (not a current dependency,
   but worth monitoring).
- Anonymous auth (`auth.anonymous.enabled = true`) behaviour changed slightly in
   Grafana 12 — viewer sessions now have stricter permission boundaries. This is
   acceptable for the development-oriented configuration.

### For Agents

- **Do not change the Grafana version in `compose.yaml` without updating this ADR.**
- All dashboard JSON must use `uid`-based datasource references (e.g., `"uid": "prometheus"`),
  never numeric datasource IDs. Grafana 12.x assigns datasource IDs dynamically.
- Datasources are provisioned via `datasources.yaml` — never add datasources through
  the Grafana UI (they will not persist across restart).
- Dashboard provisioning uses the `dashboards.yaml` provider config — new dashboard JSON
  files can be placed in `config/grafana/dashboards/` or `dashboards/`.

---

## Alternatives Considered

| Option          | Why Rejected                                                     |
| --------------- | ---------------------------------------------------------------- |
| Stay on 10.4.5  | EOL — no security patches, no access to new features             |
| Upgrade to 11.x | Would require a second upgrade to 12.x shortly after; no benefit |

---

## See Also

- Grafana 12 release notes: <https://grafana.com/docs/grafana/latest/whatsnew/>
- Grafana 11 breaking changes: <https://grafana.com/docs/grafana/v11.0/breaking-changes/>
- Provisioning documentation: <https://grafana.com/docs/grafana/latest/administration/provisioning/>
- Datasource UID reference: `.agents/skills/obs-stack/SKILL.md`
