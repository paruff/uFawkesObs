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
defines 4 datasources with fixed string UIDs (`prometheus`, `tempo`, `loki`,
`alertmanager`) — file-based provisioning, mounted into the container per
`compose.yaml`. (A 5th, `ufawkesres-postgres`, existed for DORA metrics
snapshots via the resource-plane Postgres backend; that backend was
decommissioned — DORA is SQLite-only now, see `docs/notes/res-status.md`.
A future resource plane on this Fawkes track would need its own
datasource, not a resurrection of the removed one.)

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

## Migration path — step by step

None of these steps have been executed or tested against a live Fawkes
cluster — this is a sequencing plan built from the findings above, not a
verified runbook. Each step should be validated in a non-production Fawkes
namespace before being treated as authoritative.

### Prerequisites

- A running Fawkes cluster with the `fawkes-observability` namespace
  provisioned (per `paruff/fawkes`'s own setup docs — out of scope here).
- **Export everything from uFawkesObs before touching anything on the
  Fawkes side:**
  - `dashboards/platform/*.json` and `dashboards/services/*.json` (source
    of truth is already in this repo's git history — no live export
    needed, but confirm the running Grafana instance hasn't diverged from
    committed JSON via UI edits: `allowUiUpdates: false` in
    `config/grafana/provisioning/dashboards/*.yaml` should guarantee this,
    but verify before relying on it).
  - `config/prometheus/rules/*.yml` (recording/alert rules — portable
    content, see table above).
  - Prometheus's own data if historical metrics need to survive the cut
    (`docs/KNOWN_LIMITATIONS.md` — 30-day retention only; snapshot
    `./data/prometheus` or accept the loss).
  - `dora/` snapshot data (`./data/dora/dora.db` — SQLite is the only
    backend now, see `docs/notes/res-status.md`) if DORA history needs to
    survive — see the DORA divergence note below before assuming this data
    has anywhere to go on the Fawkes side.
- A rollback point: keep the uFawkesObs Compose stack running and
  untouched until the Fawkes-side stack is validated end-to-end. Don't
  decommission Compose services as you migrate each piece — decommission
  only after full cutover validation (see Rollback below).

### Sequence

1. **Prometheus rules first** — port `config/prometheus/rules/*.yml`
   content into whatever Fawkes's chart expects (static `values.yaml` block
   or `PrometheusRule` CRD — **needs validation testing** to determine
   which). PromQL expressions themselves need no rewriting. Lowest-risk
   step: rules that don't fire yet don't break anything.
2. **Grafana datasources next** — recreate the datasource *definitions*
   (not the delivery mechanism, which differs — see Grafana findings
   above) in Fawkes's Grafana, using the same UID convention
   (`prometheus`, `tempo`) where Fawkes's own Prometheus/Tempo instances
   are the targets. Skip `loki` — there is no Fawkes equivalent (see next
   step).
3. **Dashboards without Loki panels** — import `dashboards/platform/` and
   `dashboards/services/` JSON as-is via Fawkes's Grafana provisioning.
   Before importing, **inventory which dashboards reference the `loki`
   datasource UID** (not done in this pass — a real gap, see Findings
   above) and hold those back.
4. **Loki-backed dashboards last, and only after a panel rewrite** — these
   need their log panels re-pointed at OpenSearch (Lucene/OpenSearch DSL,
   not LogQL) before they'll render correctly. Treat this as new panel
   authoring, not a config port.
5. **DORA metrics — a product decision, not a migration step.** Fawkes
   uses DevLake as its DORA engine; uFawkesObs uses its own `dora/`
   ingestion+compute pipeline. Migrating DORA dashboards means picking one
   of: (a) run uFawkesObs's `dora/` stack inside the Fawkes cluster
   alongside DevLake (duplicate pipelines, not currently how Fawkes is
   architected per its docs), or (b) rebuild the DORA dashboard panels
   against DevLake's data model and retire uFawkesObs's `dora/` pipeline
   at cutover. Do not attempt this step without that decision made first.
6. **Validate against real traffic** in the Fawkes namespace before
   touching the Compose stack — confirm scrape targets are actually being
   scraped, alert rules fire correctly, and dashboard panels show live
   data, not just that the JSON imported without error.
7. **Decommission the Compose stack** only after step 6 passes. Keep the
   exported data (step 0) until you're confident nothing needs to be
   re-imported.

### Rollback

If validation in step 6 fails or stalls partway: uFawkesObs's Compose
stack was never touched during steps 1–5 (they only add resources to the
Fawkes side), so rollback is simply "stop migrating, keep running Compose
as before" — there's no uFawkesObs-side state to revert. The only
irreversible step is #7 (decommissioning Compose); don't take it until
Fawkes-side validation is genuinely done, not just "looks right."

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
