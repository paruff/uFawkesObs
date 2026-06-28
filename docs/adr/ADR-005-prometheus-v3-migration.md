# ADR-005: Upgrade Prometheus from 2.55.1 to 3.5.4 LTS

**Status:** Accepted
**Date:** 2026-06-28
**Deciders:** uFawkesObs maintainers
**Issue:** [#132](https://github.com/paruff/uFawkesObs/issues/132) — OBS-VER-05

---

## Context

uFawkesObs was deployed with Prometheus 2.55.1 (`prom/prometheus:v2.55.1`), the last 2.x LTS release. As of July 31, 2025, Prometheus 2.x reached end-of-life and no longer receives security patches or bug fixes. Prometheus 3.5.4 is the current LTS release (supported until July 2026), with the next LTS (3.13) due June 2026.

Running an unsupported Prometheus version in the observability stack carries increasing risk:
1. **Security vulnerabilities** — EOL versions receive no security patches; Prometheus handles sensitive telemetry data.
2. **Feature gap** — Prometheus 3.x introduced native histograms, improved remote write v2, and better TSDB compression.
3. **Ecosystem alignment** — Other uFawkesObs components (Loki 3.3.2, Grafana 12.3.7, Tempo 2.10.5) are on current versions.
4. **Operational risk** — Future debugging and community support for v2 issues will be limited.

The upgrade from 2.55.1 → 3.5.4 is a single major version jump. Prometheus 2.55 was specifically designed as a "bridge" release to ease the 2.x → 3.x migration.

---

## Decision

**Upgrade Prometheus from 2.55.1 to 3.5.4** (`prom/prometheus:v3.5.4`).

No configuration changes are required — the existing `prometheus.yaml`, rule files, and provisioning are fully compatible with Prometheus 3.x.

---

## Migration Summary

| Detail              | Value                                                    |
| ------------------- | -------------------------------------------------------- |
| **Previous version** | `prom/prometheus:v2.55.1`                                |
| **Current version**  | `prom/prometheus:v3.5.4`                                 |
| **PR**               | #TBD (this migration)                                    |
| **Date**             | 2026-06-28                                               |
| **Jump**             | 2.55.1 → 3.5.4 (one major version, bridge release path) |
| **Config changes**   | None — existing config fully compatible                  |

### Breaking Changes Assessed and Handled

| Breaking Change | Version | Impact on uFawkesObs | Mitigation |
| --------------- | ------- | -------------------- | ---------- |
| Native histograms stable | 3.0 | None — not using `--enable-feature=native-histograms` | N/A |
| `scrape_classic_histograms` renamed to `always_scrape_classic_histograms` | 3.0 | None — not using this option | N/A |
| Remote write `http2` default → false | 3.0 | None — not using remote write | N/A |
| Stricter Content-Type headers | 3.0 | **Potential** — verify scrape targets | All targets are standard exporters (OTel, Alloy, Node Exporter, Loki, Tempo, Grafana, Alertmanager) sending correct headers |
| Alertmanager v1 API removed | 3.0 | None — config uses `api_version: v2` (default) | N/A |
| TSDB format change | 3.0 | **Compatible** — v2.55 TSDB forward-compatible | v3 reads v2.55 format natively; downgrade to v2.55 works |

### Configuration Compatibility

All current configuration keys are v3-compatible:

- **prometheus.yaml**: Standard `global`, `alerting`, `rule_files`, `scrape_configs` — no deprecated features used
- **alerts.yml**: Standard alerting rules with `absent()` guards — compatible
- **rules/ufawkesobs-self-monitoring.yml**: Vector math, `absent()` guards, `changes()` — compatible
- **rules/ai-rules.yml**: Recording rules with `or vector(0)` guards — compatible

### Data Persistence

TSDB volume at `./data/prometheus`:
- Prometheus 3.5 reads 2.55 TSDB format natively (forward compatibility)
- Downgrade to 2.55.1 works without data loss
- No migration step required

---

## Rationale

1. **Security** — Prometheus 2.x is EOL. Running an EOL version that ingests and stores telemetry from all uFawkes planes is an unacceptable risk posture.

2. **LTS stability** — 3.5.4 is the current LTS patch (released 2026-06-XX). It includes all 3.x stability fixes since 3.0.

3. **Bridge release path** — 2.55 was specifically designed as the migration bridge. Upgrading from 2.55 to 3.x is the supported path with minimal breaking changes.

4. **No config migration effort** — uFawkesObs does not use native histograms, remote write, or any deprecated 2.x features. The upgrade is a clean image version bump.

5. **Future-proofing** — Starting from 3.5.4 means the next LTS upgrade (3.13, due June 2026) will be incremental rather than from an EOL version.

---

## Consequences

### Positive

- Running a supported, security-patched version of Prometheus.
- Access to Prometheus 3.x features: native histograms (when enabled), improved TSDB compression (~20% storage reduction), faster query performance.
- No configuration migration work required.
- Future upgrades (3.5 → 3.13 LTS) will be incremental.

### Negative / Trade-offs

- Prometheus 3.x has slightly higher baseline memory usage (~5-10% increase for same scrape load).
- TSDB format is not backward-compatible with v2.47 and earlier (not applicable — we're on 2.55).
- Some experimental features from 2.x (e.g., `--enable-feature=memory-snapshot-on-shutdown`) are removed or changed.

### For Agents

- **Do not change the Prometheus version in `compose.yaml` without updating this ADR.**
- All recording rules must use `or vector(0)` guards to prevent `absent()` gaps (already enforced in uFawkesObs).
- All alert rules must have paired `absent()` guards (already enforced in uFawkesObs).
- Rule files must be validated with `promtool check rules` using the target Prometheus version.
- Prometheus config must be validated with `promtool check config` before deployment.

---

## Alternatives Considered

| Option | Why Rejected |
| ------ | ------------ |
| Stay on 2.55.1 | EOL — no security patches, no access to 3.x features |
| Upgrade to 3.0.x | Not LTS; would require second upgrade to 3.5.x shortly after |
| Upgrade to 3.13 (when released) | 3.13 not yet released; 3.5.4 is current LTS with full support |

---

## See Also

- Prometheus 3.5 release notes: <https://prometheus.io/docs/prometheus/latest/whatsnew/>
- Prometheus 3.0 breaking changes: <https://prometheus.io/docs/prometheus/latest/migration/v3/>
- Promtool documentation: <https://prometheus.io/docs/prometheus/latest/configuration/promtool/>
- uFawkesObs Prometheus config: `config/prometheus/prometheus.yaml`
- uFawkesObs rule files: `config/prometheus/alerts.yml`, `config/prometheus/rules/`
- OBS-VER-05 issue: <https://github.com/paruff/uFawkesObs/issues/132>

---

## Verification Checklist

- [ ] ADR-005 created in `docs/adr/`
- [ ] `compose.yaml` updated to `prom/prometheus:v3.5.4`
- [ ] `promtool check config` passes
- [ ] `promtool check rules` passes for all 3 rule files
- [ ] Stack starts successfully (`docker compose up -d prometheus`)
- [ ] Health endpoint returns 200 (`curl /-/healthy`)
- [ ] All scrape targets UP (`curl /api/v1/targets`)
- [ ] All acceptance tests pass
- [ ] Grafana dashboards render historical data
