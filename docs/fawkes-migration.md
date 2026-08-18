# Fawkes Migration Notes — Prometheus/Grafana/Dashboard Portability

> Task 4 of the uFawkesObs suite-alignment brief. Assesses whether this
> repo's observability config is portable to Fawkes (the Kubernetes track).
> Findings only — no migration has been attempted or tested here.

## What was actually checked

Fetched `docs/ARCHITECTURE.md` from `paruff/fawkes` (`main` branch,
`https://raw.githubusercontent.com/paruff/fawkes/main/docs/ARCHITECTURE.md`,
437 lines) and read it directly. The brief's framing — "Prometheus/Grafana/
Tempo via OpenTelemetry Operator" — is **only partially confirmed**: the doc
confirms Prometheus, Grafana, and Tempo, and confirms services export via
the OpenTelemetry SDK to an in-cluster **OpenTelemetry Collector**. It does
**not** mention an "OpenTelemetry Operator" (the Kubernetes CRD-based
operator) anywhere — deployment is described as Helm charts (`charts/`,
`platform/`) applied via ArgoCD (GitOps), not Operator-managed CRDs. This is
a discrepancy from the brief worth flagging rather than silently accepting:
either the Operator is used in a way the architecture doc doesn't call out,
or the brief's premise on that specific point is inaccurate. Not resolved
here — needs a direct check of `paruff/fawkes`'s `charts/` or `platform/`
directory contents, which was out of scope for this pass.

Compared against this repo's `config/prometheus/`, `config/grafana/`, and
`dashboards/platform/` + `dashboards/services/` (23 dashboard JSON files,
all schemaVersion 39 per `AGENTS.md` §4).

## Findings by area

### Prometheus

**uFawkesObs:** `config/prometheus/prometheus.yaml` (scrape config) +
`config/prometheus/alerts.yml` + `config/prometheus/rules/*.yml` (4 recording/
alert rule files, e.g. `ufawkesobs-dora-metrics.yml`). Scrape targets are
Compose service names (`prometheus:9090`-style, per `AGENTS.md` §4 — "scrape
targets must match actual service names in compose.yaml").

**Fawkes:** Runs in the `fawkes-observability` namespace, deployed via Helm
chart, per the architecture doc's namespace table. No mention of whether
scrape config is static (a Helm `values.yaml` block) or CRD-driven
(`ServiceMonitor`/`PodMonitor`, implying the Prometheus Operator /
kube-prometheus-stack) — **unresolved, needs validation testing** against
the actual `paruff/fawkes` chart values.

**Assessment:**
- Recording/alert rule *content* (PromQL expressions in `config/prometheus/
  rules/*.yml`) is portable as-is — PromQL doesn't change between Compose
  and Kubernetes. **Portable.**
- Scrape config itself is **not** portable as-is — Compose service-name
  targets (`prometheus.yaml`) would need to become either static K8s DNS
  targets or `ServiceMonitor` CRDs, depending on which pattern Fawkes's
  chart actually uses. **Needs conversion; exact target format needs
  validation testing.**

### Grafana

**uFawkesObs:** `config/grafana/provisioning/datasources/datasources.yaml`
defines 5 datasources with fixed string UIDs (`prometheus`, `tempo`, `loki`,
`alertmanager`, `ufawkesres-postgres`) — file-based provisioning, mounted
into the container per `compose.yaml`.

**Fawkes:** Grafana runs in-cluster per the namespace table
(`fawkes-observability`), deployed via Helm/ArgoCD. The architecture doc
doesn't show its datasource provisioning mechanism (Helm values block vs.
ConfigMap vs. Grafana Operator CRD) — **unverified**.

**Assessment:**
- The datasource *definitions themselves* (type, `jsonData`, UID
  convention) are portable in content — Grafana's datasource schema is the
  same regardless of host platform. **Portable in content.**
- The *delivery mechanism* (file provisioning vs. Helm values vs. CRD) is
  **not** portable as-is and needs conversion to whatever Fawkes's chart
  expects. **Needs conversion; exact mechanism needs validation testing.**
- One concrete divergence: uFawkesObs's `Loki` datasource has no Fawkes
  equivalent — Fawkes's architecture doc uses **OpenSearch** (via Fluent
  Bit) for logs, not Loki. A dashboard panel querying the `loki` datasource
  UID would need to be re-pointed at an OpenSearch datasource, which is a
  different query language (LogQL vs. Lucene/OpenSearch DSL), not just a
  UID rename. **Not portable — requires panel-level rework, not just
  config conversion.**

### Dashboards

**uFawkesObs:** 23 JSON files under `dashboards/platform/` and
`dashboards/services/`, all `schemaVersion: 39`, referencing datasources by
UID string (`prometheus`, `tempo`, `loki`, etc., per `AGENTS.md` §4).

**Fawkes:** No dashboard JSON or schemaVersion requirement is documented in
`docs/ARCHITECTURE.md` — the doc describes DevLake producing DORA
dashboards in Grafana, not the dashboard provisioning mechanism itself.
**Unverified — needs validation testing** against whatever's actually in
`paruff/fawkes`'s Grafana provisioning config, if any exists yet.

**Assessment:**
- Grafana's dashboard JSON schema (schemaVersion 39, panel definitions,
  variables) is platform-agnostic — dashboards querying only Prometheus/
  Tempo panels should import into any Grafana 12.x instance with matching
  datasource UIDs, Fawkes included. **Likely portable, but not actually
  tested against a running Fawkes instance — needs validation testing.**
- Any dashboard with Loki-backed log panels needs the OpenSearch rework
  noted above before it would render correctly on Fawkes. Not all 23
  dashboards were individually audited for Loki panel usage in this pass —
  **needs a follow-up inventory** of which specific dashboards use the
  `loki` datasource UID.

### DORA metrics — architectural divergence, not just config

Worth calling out explicitly: uFawkesObs computes DORA metrics itself (the
`dora/` directory, consolidated from the former uFawkesDORA repo) and writes
snapshots to Postgres/SQLite plus a Prometheus pushgateway. Fawkes's
architecture doc describes **DevLake** as the DORA metrics engine, feeding
Grafana directly via its own API (`DevLake->>Grafana: expose metrics via
API`). These are two different DORA pipelines, not the same pipeline on two
hosting platforms. Migrating uFawkesObs's DORA dashboards to Fawkes would
mean either (a) running uFawkesObs's own `dora/` ingestion+compute stack
inside the Fawkes cluster (not how Fawkes is currently architected, per the
doc), or (b) re-pointing the DORA dashboard panels at DevLake's data model
instead — a dashboard content rewrite, not a config port. **Not portable —
needs a product decision on which DORA pipeline Fawkes-tier teams should
use, out of scope for this doc.**

## Summary table

| Area | Portable | Needs conversion | Unverified |
|---|---|---|---|
| PromQL rule content | ✅ | | |
| Prometheus scrape config format | | ✅ (Compose names → K8s) | ✅ (static vs. CRD) |
| Grafana datasource *content* | ✅ | | |
| Grafana datasource *delivery mechanism* | | ✅ | ✅ |
| Dashboard JSON (Prometheus/Tempo panels) | likely | | ✅ (not tested live) |
| Dashboard JSON (Loki panels) | | ✅ (Loki → OpenSearch rework) | |
| DORA dashboards/pipeline | | | ✅ (architectural — needs product decision) |

## When to graduate to Fawkes

Reusable as a standalone checklist (e.g. for ufawkes.dev). uFawkesObs is
the right fit until most of these start being true — Fawkes is the better
fit once several apply:

- **Team size** exceeds the 3–15 person range uFawkesObs is designed for
  (per its own README's "What This Is" section).
- **Multi-node** deployment is needed — uFawkesObs's `compose.yaml` runs
  everything on a single Docker host by design (`docs/KNOWN_LIMITATIONS.md`
  — "Single-Node Deployment Only"); Fawkes runs on Kubernetes, which is
  built for multi-node from the start.
- **GitOps pull-based reconciliation** is required. uFawkesObs's current
  model is SSH push + `make up` (`AGENTS.md` §8: "Progressive delivery is
  aspirational. The current model is SSH push with `make up`. A staged
  model (canary → staging → production) should be designed before
  uFawkesObs serves production traffic"). Fawkes uses ArgoCD, a real
  pull-based GitOps controller, out of the box.
- **High availability** is a requirement for any individual service —
  uFawkesObs has no built-in HA story (`docs/KNOWN_LIMITATIONS.md`);
  Kubernetes gives you replica sets, pod disruption budgets, and
  node-failure tolerance for free.
- **Centralized secrets management** beyond `.env` files is needed — Fawkes
  integrates Vault and the External Secrets Operator; uFawkesObs's secret
  handling is a gitignored `.env` file, appropriate for a single trusted
  host, not a multi-tenant or compliance-driven environment.
- **A full platform team surface** is wanted — Backstage developer portal,
  policy-as-code security scanning (SonarQube, Trivy), and a real CI/CD
  engine (Jenkins + ArgoCD) are all part of Fawkes's Tier 1/2 stack; none
  of that exists in uFawkesObs, which is observability-only by design.

If none of the above apply yet, uFawkesObs's Compose-based model is very
likely still the right tier — don't graduate just because Kubernetes
exists.
