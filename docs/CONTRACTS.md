# uFawkesObs's Contract Surface

> **Scope:** This document describes what uFawkesObs currently expects to
> *receive* from other planes and instrumented services, based on its actual
> implementation as of this writing. It is not a bilateral spec other planes
> are bound by, and it is not the suite's shared source of truth — see
> "Where this goes next" at the end.

uFawkesObs is the consumer side of two contracts:

1. **DORA events** — deployment, PR, incident, and rework events POSTed to
   the ingestion API (`dora/ingestion/`), which now lives in this repo (the
   standalone uFawkesDORA repo was consolidated in — see `AGENTS.md` §10).
2. **OTLP telemetry** — traces, metrics, and logs sent by instrumented
   services to the OpenTelemetry Collector (`config/otel/collector.yaml`).

---

## 1. DORA Event Ingestion

### Endpoints

Implemented in `dora/ingestion/api/main.py`. The service listens on
`127.0.0.1:8088` by default (`compose.yaml`, `dora-api` service, `dora`
profile).

| Method | Path           | Purpose                                              |
| ------ | -------------- | ----------------------------------------------------- |
| `POST` | `/event`       | Accept one event, validate, enqueue. `201` on success. |
| `POST` | `/event/batch` | Accept multiple events in one transaction — all-or-nothing: if any event fails validation, none are enqueued. `201` on success. |
| `GET`  | `/health`      | `{"status": "ok", "queue_depth": N}`.                 |

Validation failures return `422` with field-level detail
(`dora/ingestion/api/validator.py`):

```json
{
  "detail": [
    {"loc": ["body", "environment"], "msg": "'environment' is a required property", "type": "value_error"}
  ]
}
```

**Authentication: none is currently enforced.** `dora/collectors/generic/curl-examples.sh`
documents an optional `DORA_API_KEY` bearer token ("if auth is enabled"),
and collector scripts pass it through when set — but `main.py` has no
`Authorization` header check anywhere. Treat this as a documented gap, not
an implemented option, until it's added (see §4).

### Event types and required fields

Each event is a flat JSON object validated against a Draft-07 schema in
`dora/events/`. `event_type` is the routing discriminant
(`dora/ingestion/api/validator.py:EVENT_TYPE_SCHEMA_MAP`), and every schema
sets `"additionalProperties": false` — extra fields are rejected, not
ignored.

#### `deployment` — `dora/events/deployment-event.schema.json`

Drives Deployment Frequency, Lead Time, Change Failure Rate, and FDRT.

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | Pattern `^\d+\.\d+$`, e.g. `"1.0"` |
| `event_type` | const `"deployment"` | yes | |
| `repo` | string | yes | e.g. `"org/repo-name"` |
| `service` | string | yes | Component name within the repo |
| `environment` | string | yes | e.g. `"production"`, `"staging"` |
| `commit_sha` | string | yes | Full 40-char SHA (`^[0-9a-f]{40}$`) |
| `deployed_at` | string (date-time) | yes | ISO 8601 |
| `status` | enum | yes | `success` \| `failed` \| `rollback` |
| `pipeline_url` | string (uri) | yes | Link to the CI run |
| `deploy_duration_seconds` | integer ≥ 0 | no | |
| `ai_assisted` | boolean | no | |

#### `pr` — `dora/events/pr-event.schema.json`

Drives Lead Time and PR throughput.

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | |
| `event_type` | const `"pr"` | yes | |
| `repo` | string | yes | |
| `pr_number` | integer ≥ 1 | yes | |
| `commit_sha` | string | yes | 40-char SHA |
| `status` | enum | yes | `opened` \| `merged` \| `closed` |
| `occurred_at` | string (date-time) | yes | |
| `first_commit_at` | string (date-time) | yes | |
| `lines_added` / `lines_deleted` | integer ≥ 0 | no | |
| `ai_assisted` | boolean | no | |

#### `incident` — `dora/events/incident-event.schema.json`

Drives Time to Restore / FDRT.

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | |
| `event_type` | const `"incident"` | yes | |
| `incident_id` | string | yes | e.g. a PagerDuty ID |
| `repo` | string | yes | |
| `service` | string | yes | |
| `status` | enum | yes | `opened` \| `resolved` |
| `occurred_at` | string (date-time) | yes | |
| `linked_deployment_sha` | string | no | 40-char SHA, if known |
| `severity` | string | no | e.g. `"SEV1"` |

#### `rework` — `dora/events/rework-event.schema.json`

Drives Rework Rate — deployments that are remediation, not forward
progress.

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | |
| `event_type` | const `"rework"` | yes | |
| `repo` | string | yes | |
| `deployment_sha` | string | yes | 40-char SHA |
| `rework_type` | enum | yes | `hotfix` \| `rollback` \| `patch` |
| `triggered_at` | string (date-time) | yes | |
| `user_visible` | boolean | yes | Distinguishes user-visible rework from internal/corrective changes |

### Working examples

`dora/collectors/` has concrete, tested payload examples per platform —
these are the actual contract in executable form, more reliable than any
prose summary:

- `dora/collectors/github/dora-deployment-event.yml` — reusable GitHub
  Actions workflow (`workflow_call`) that builds and POSTs a `deployment`
  event from `github.sha`, `github.event.head_commit.timestamp`, etc.
- `dora/collectors/github/dora-pr-event.yml` — same, for `pr` events.
- `dora/collectors/generic/curl-examples.sh` — raw `curl` examples for all
  four event types, plus a field-mapping table for GitLab CI, CircleCI,
  Jenkins, and Woodpecker CI variable names.
- `dora/collectors/woodpecker/pipeline-snippet.yml` — Woodpecker-specific
  pipeline step.
- `dora/collectors/manual-incident/declare-incident.sh` /
  `resolve-incident.sh` — scripts for manually emitting `incident` events
  (opened/resolved) outside of CI, e.g. from an on-call tool.

### Queueing (implementation detail, not part of the wire contract)

`dora/ingestion/api/queue.py` is a thin facade over `queue_sqlite.py` —
SQLite is the only backend. `POST /event` enqueues synchronously and
returns immediately — `dora/compute/` processes the queue asynchronously
to compute the five DORA metrics.

---

## 2. OTLP Telemetry Conventions

### Receivers

Two Collector instances run, both accepting standard OTLP on the same
ports (`config/otel/collector.yaml` for `core`, `config/otel/collector-dora.yaml`
for the `dora` profile's `otel-collector-dora` service):

| Protocol | Endpoint |
|---|---|
| OTLP gRPC | `0.0.0.0:4317` |
| OTLP HTTP | `0.0.0.0:4318` |

Send traces, metrics, and logs to whichever collector instance is
appropriate for your service — there is no schema-level difference between
the two receivers, only downstream routing differs (see below).

### No enforced resource-attribute schema

Neither collector config declares a `resourcedetection` or `schema`
processor that rejects telemetry missing specific resource attributes
(e.g. `service.name`). Any well-formed OTLP payload is accepted; Grafana
dashboards and Prometheus labels will simply be sparser if conventional
attributes like `service.name` are omitted. There is no required minimum
attribute set enforced by Obs today — this is a gap if strict conventions
are wanted later, not a currently-implemented requirement.

### Metric routing conventions (`config/otel/collector.yaml`)

The main collector has two metrics pipelines:

- `metrics` — the default pipeline; every metric received goes to
  Prometheus (`app_metrics` namespace) and `debug` (stdout logging).
- `metrics/ai` — a **name-based filter**, not an attribute-based one: any
  metric whose name matches `gen_ai\..*`, `llm\..*`, `openllmetry\..*`, or
  `ai\..*` (case-sensitive regex, `filter/ai` processor) additionally gets
  routed through `attributes/ai`, which inserts two fixed labels
  (`ai.environment=development`, `ai.platform=fawkes-idp`) before export.
  **Convention for AI-observability metrics: prefix the metric name with
  one of those four namespaces** if you want it captured by this pipeline.

Traces always export to Tempo (`otlp/tempo`, insecure gRPC on `tempo:4317`)
and logs always export to Loki (`loki`, HTTP push to
`loki:3100/loki/api/v1/push`) — no filtering on either.

### `otel-collector-dora` (`config/otel/collector-dora.yaml`) — not deployed

> **The container was removed.** Nothing in this repo ever emitted the
> `dora.*` / `cicd.*` signals it filtered on (issue #266), Prometheus never
> scraped it, and it crash-looped on an unresolvable `tempo:4317` — Tempo is
> in the `core` profile while this service was in `dora`. Those errors were
> being collected into Loki by Alloy.
>
> The config below is **retained as inert configuration**, not running
> infrastructure, so the OTLP-native DORA path described in ADR-006 can be
> rebuilt without redesigning it. DORA ingestion today is REST-only via
> `dora-api` (`POST /event`).

Same receiver/exporter shape as the main collector, plus a DORA-specific
metrics pipeline:

- `metrics/dora` — filters on metric name regex
  `dora\..*` / `cicd\..*` / `deployment\..*` / `incident\..*`
  (`filter/dora`), inserts `dora.environment=production` /
  `dora.platform=fawkes-idp` (`attributes/dora`), then exports to
  **both** Prometheus and an `otlp/dora` exporter pointed at
  `${OTEL_EXPORTER_OTLP_ENDPOINT}` (defaults to
  `http://ufawkesdora-ingestion:4318` per `compose.yaml`).

**Discrepancy found while writing this doc:** the `otlp/dora` exporter
forwards matched metrics via OTLP to `ufawkesdora-ingestion:4318` — but
`dora/ingestion/api/main.py` (the `dora-api`/`ufawkesdora-ingestion`
service) is a REST-only FastAPI app exposing `/event`, `/event/batch`, and
`/health` on port 8088. Nothing in `dora/ingestion/` implements an OTLP
receiver on port 4318 or anywhere else. This exporter target currently has
nothing listening on it — DORA metrics reach the ingestion API exclusively
via the REST `POST /event` contract described in §1, not via OTLP metric
forwarding, despite the collector being wired as though the latter were
live. This should either be removed (dead config) or implemented
(an OTLP-to-event-schema bridge) — flagging it here rather than describing
it as working.

---

## Where this goes next

The plan (not yet implemented) is for **uFawkesPipe** to host the
suite-wide, machine-readable version of these contracts — the JSON
Schemas as source of truth, likely alongside its own CI/CD event emission
code — with **ufawkes.dev** rendering the human-readable page from that
shared source. This document is Obs's own snapshot of what it currently
implements as the consumer, not that shared location; if Pipe's future
schemas diverge from `dora/events/*.schema.json`, this doc (and the
schemas here) are what Obs actually enforces until reconciled.
